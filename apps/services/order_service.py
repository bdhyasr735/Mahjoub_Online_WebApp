# coding: utf-8
# 📂 apps/services/order_service.py

import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy import or_, cast, Integer, String
from .graphql_client import GraphQLClient


class OrderService:
    """خدمة إدارة الطلبات والمزامنة مع واجهة GraphQL وقاعدة البيانات المحلية"""

    def __init__(self, client: GraphQLClient):
        self.client = client

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.query_file_path = os.path.join(current_dir, 'orders_queries.graphql')

        try:
            with open(self.query_file_path, 'r', encoding='utf-8') as f:
                self.queries_content = f.read()
        except FileNotFoundError:
            print("⚠️ [OrderService]: لم يتم العثور على ملف الاستعلامات")
            self.queries_content = ""

    def _extract_query(self, query_name: str) -> str:
        """استخراج استعلام معين من ملف الاستعلامات"""
        if not self.queries_content:
            return ""

        lines = self.queries_content.split('\n')
        result = []
        found = False
        brace_count = 0

        for line in lines:
            if f"query {query_name}" in line or f"mutation {query_name}" in line:
                found = True

            if found:
                result.append(line)
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0 and len(result) > 1:
                    break

        return '\n'.join(result)

    def _save_orders_to_db(self, orders_data: List[Dict[str, Any]]):
        """دالة مساعدة مجمعة لحفظ وتحديث الطلبات وعناصرها مع دعم تعدد الموردين المحليين"""
        try:
            from apps.models.orders_db import Order
            from apps.models.order_items_db import OrderItem
            from apps.models.product_supplier_map import ProductSupplierMapping
            from apps.extensions import db

            for order in orders_data:
                if not order or not isinstance(order, dict):
                    continue
                qid = order.get('_id') or order.get('id')
                if not qid:
                    continue

                items_list = order.get('items') or []
                
                # استخراج حالة الطلب بشكل آمن
                status_obj = order.get('status') or {}
                if isinstance(status_obj, dict):
                    status_code = status_obj.get('code') or 'pending'
                    status_title = status_obj.get('title') or 'قيد الانتظار'
                else:
                    status_code = str(status_obj) if status_obj else 'pending'
                    status_title = 'قيد الانتظار'

                # استخراج اسم العميل بشكل آمن (تم التعديل هنا)
                account_outer = order.get('account') or {}
                account_inner = account_outer.get('account') or {}
                raw_fullname = account_inner.get('fullname')

                if raw_fullname and raw_fullname.strip():
                    customer_name = raw_fullname
                else:
                    # إذا لم يوجد اسم، نحدد النوع
                    if order.get('type') == 'guest':
                        customer_name = 'زائر'
                    else:
                        customer_name = 'عميل غير معروف'

                # استخراج الحالة المالية والإجمالي
                is_paid = order.get('isPaid', False)
                total_price = order.get('totalPrice', 0.0) or 0.0

                # استخراج وتنسيق تاريخ الإنشاء
                created_at_str = order.get('createdAt')
                created_at = datetime.utcnow()
                if created_at_str:
                    try:
                        clean_date_str = created_at_str.replace('Z', '').split('+')[0]
                        created_at = datetime.fromisoformat(clean_date_str)
                    except Exception:
                        pass

                # البحث عن الطلب محلياً
                existing_order = Order.query.filter_by(id=qid).first()

                # توليد الرقم التسلسلي للطلب الجديد
                last_order = db.session.query(Order).order_by(cast(Order.order_number, Integer).desc()).first()
                if last_order and last_order.order_number:
                    try:
                        next_number = int(last_order.order_number) + 1
                    except (ValueError, TypeError):
                        next_number = 1000000235
                else:
                    next_number = 1000000235

                if existing_order:
                    existing_order.status_code = status_code
                    existing_order.status_title = status_title
                    existing_order.customer_name = customer_name
                    existing_order.is_paid = is_paid
                    existing_order.total_price = total_price
                    existing_order.created_at = created_at

                    # حذف العناصر القديمة لإعادة إدراجها بالتحديثات الجديدة
                    OrderItem.query.filter_by(order_id=existing_order.id).delete()
                else:
                    existing_order = Order(
                        id=qid,
                        status_code=status_code,
                        status_title=status_title,
                        customer_name=customer_name,
                        is_paid=is_paid,
                        total_price=total_price,
                        order_number=next_number,
                        created_at=created_at
                    )
                    db.session.add(existing_order)
                    db.session.flush()

                # معالجة عناصر الطلب وتوزيع الموردين المحليين بدقة على مستوى كل عنصر
                primary_supplier_id = None
                for item in items_list:
                    if not item:
                        continue
                    prod_data = item.get('productData') or {}
                    qty = item.get('quantity', 1) or 1
                    price = item.get('price', 0.0) or 0.0
                    prod_id = item.get('productId', '')

                    product_name = prod_data.get('title') or (f"منتج ({prod_id[:8]})" if prod_id else "منتج غير معروف")
                    sku = prod_data.get('slug') or prod_data.get('sku') or prod_id

                    # البحث عن المورد المحلي الخاص بهذا المنتج عبر جدول الربط
                    item_supplier_id = None
                    if prod_id:
                        mapping = ProductSupplierMapping.query.filter_by(product_qid=prod_id).first()
                        if mapping:
                            item_supplier_id = mapping.supplier_id

                    # تعيين أول مورد رئيسي للطلب كمرجع أساسي إن لم يُحدد مسبقاً
                    if primary_supplier_id is None and item_supplier_id is not None:
                        primary_supplier_id = item_supplier_id

                    new_item = OrderItem(
                        order_id=existing_order.id,
                        supplier_id=item_supplier_id,
                        product_name=product_name,
                        quantity=qty,
                        price=price
                    )
                    db.session.add(new_item)

                # تحديث المورد الرئيسي للطلب
                existing_order.supplier_id = primary_supplier_id

                db.session.commit()
        except Exception as db_err:
            print(f"⚠️ [OrderService] خطأ تفصيلي أثناء حفظ الطلبات محلياً: {db_err}")
            db.session.rollback()

    def get_order(self, qid: str) -> Optional[Dict[str, Any]]:
        """جلب تفاصيل الطلب من API باستخدام المعرف qid"""
        query = self._extract_query("FindOrderById")
        try:
            result = self.client.execute(query, {"id": qid}, operation_name="FindOrderById")
            if result and 'findOrderById' in result:
                res_data = result['findOrderById']
                if isinstance(res_data, dict) and 'data' in res_data and res_data['data']:
                    return res_data['data']
                return res_data
            return None
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في جلب الطلب {qid}: {e}")
            return None

    def sync_single_order(self, qid: str):
        """⚡ جلب طلب مفرد من GraphQL وتخزينه محلياً فوراً ثم إرجاع الكائن"""
        order_data = self.get_order(qid)
        if order_data:
            self._save_orders_to_db([order_data])

        from apps.models.orders_db import Order
        return Order.query.get(qid)

    def get_order_by_id(self, qid: str):
        """اسم مستعار (Alias) لـ sync_single_order لضمان عمل كافة الاستدعاءات"""
        return self.sync_single_order(qid)

    def get_all_orders(
        self,
        page: int = 1,
        per_page: int = 10,
        supplier_id: str = None,
        status: str = None,
        search: str = None,
        date_from: str = None,
        date_to: str = None
    ) -> Dict[str, Any]:
        """جلب قائمة الطلبات ودمجها وتخزينها في قاعدة البيانات المحلية"""
        input_data = {"page": page, "limit": per_page}
        if supplier_id: input_data["supplierId"] = supplier_id
        if status: input_data["status"] = status
        if search: input_data["search"] = search
        if date_from: input_data["dateFrom"] = date_from
        if date_to: input_data["dateTo"] = date_to

        query = self._extract_query("FindAllOrders")
        try:
            result = self.client.execute(query, {"input": input_data}, operation_name="FindAllOrders")

            orders_data = []
            pagination_data = {
                "totalItems": 0,
                "totalPages": 1,
                "currentPage": page,
                "limit": per_page,
                "hasNextPage": False
            }

            if result and 'findAllOrders' in result:
                orders_data = result['findAllOrders'].get('data', []) or []
                pagination_data = result['findAllOrders'].get('pagination', {}) or {}

                # حفظ دفعة الطلبات محلياً
                self._save_orders_to_db(orders_data)

            return {
                "data": orders_data,
                "pagination": pagination_data
            }
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في جلب الطلبات: {e}")
            return {
                "data": [],
                "pagination": {
                    "totalItems": 0,
                    "totalPages": 1,
                    "currentPage": page,
                    "limit": per_page,
                    "hasNextPage": False
                }
            }

    def get_local_orders(
        self,
        page: int = 1,
        per_page: int = 10,
        supplier_id: int = None,
        status: str = None,
        search: str = None,
        date_from: str = None,
        date_to: str = None
    ) -> Dict[str, Any]:
        """جلب الطلبات من قاعدة البيانات المحلية مع الترقيم والفلترة مع دعم عرض الطلبات للمورد بناءً على عناصره"""
        from apps.models.orders_db import Order
        from apps.models.order_items_db import OrderItem
        from apps.extensions import db

        try:
            query = db.session.query(Order)

            if supplier_id is not None:
                # التحقق مما إذا كان المورد مرتبطاً بالطلب رئيسياً أو بأي عنصر داخل الطلب
                query = query.filter(
                    or_(
                        Order.supplier_id == supplier_id,
                        Order.items.any(OrderItem.supplier_id == supplier_id)
                    )
                )
            if status:
                query = query.filter(Order.status_code == status)
            if date_from:
                query = query.filter(Order.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
            if date_to:
                query = query.filter(Order.created_at <= datetime.strptime(date_to, '%Y-%m-%d'))
            if search:
                query = query.filter(or_(
                    Order.id.ilike(f'%{search}%'),
                    cast(Order.order_number, String).ilike(f'%{search}%'),
                    Order.customer_name.ilike(f'%{search}%')
                ))

            total_items = query.count()
            total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 1

            # الترتيب حسب تاريخ الإنشاء (الأحدث أولاً)
            orders = query.order_by(Order.created_at.desc(), cast(Order.order_number, Integer).desc()).offset((page - 1) * per_page).limit(per_page).all()

            orders_data = []
            for order in orders:
                try:
                    order_dict = order.to_dict()
                    if hasattr(order, 'supplier') and order.supplier:
                        order_dict['supplier_name'] = order.supplier.trade_name
                    else:
                        order_dict['supplier_name'] = 'غير مرتبط'
                    orders_data.append(order_dict)
                except Exception as ser_err:
                    print(f"⚠️ [OrderService] فشل تحويل الطلب {order.id} إلى JSON: {ser_err}")
                    continue

            return {
                'data': orders_data,
                'pagination': {
                    'totalItems': total_items,
                    'totalPages': total_pages,
                    'currentPage': page,
                    'limit': per_page,
                    'hasNextPage': page < total_pages
                }
            }
        except Exception as e:
            print(f"❌ [OrderService] خطأ حرج أثناء جلب الطلبات المحلية: {e}")
            return {
                'data': [],
                'pagination': {
                    'totalItems': 0,
                    'totalPages': 1,
                    'currentPage': page,
                    'limit': per_page,
                    'hasNextPage': False
                }
            }

    def create_order(self, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        mutation = self._extract_query("CreateOrder")
        try:
            result = self.client.execute(mutation, {"input": input_data}, operation_name="CreateOrder")
            return result.get('createOrder') if result else None
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في إنشاء الطلب: {e}")
            return None

    def update_order_status(self, qid: str, status: str) -> Optional[Dict[str, Any]]:
        """تحديث حالة الطلب عبر GraphQL"""
        mutation = self._extract_query("ChangeOrderStatus")
        try:
            variables = {
                "input": {
                    "orderId": str(qid),
                    "status": str(status)
                }
            }
            result = self.client.execute(mutation, variables, operation_name="ChangeOrderStatus")
            return result.get('changeOrderStatus') if result else None
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في تحديث حالة الطلب {qid}: {e}")
            return None

    def update_financial_status(self, qid: str, financial_status: str) -> Optional[Dict[str, Any]]:
        """تحديث الحالة المالية للطلب عبر GraphQL"""
        mutation = self._extract_query("ChangeFinancialStatus")
        if not mutation:
            return None
        try:
            variables = {
                "input": {
                    "orderId": str(qid),
                    "financialStatus": str(financial_status)
                }
            }
            result = self.client.execute(mutation, variables, operation_name="ChangeFinancialStatus")
            return result.get('changeFinancialStatus') if result else None
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في تحديث الحالة المالية للطلب {qid}: {e}")
            return None

    def update_fulfillment_status(self, qid: str, fulfillment_status: str) -> Optional[Dict[str, Any]]:
        """تحديث حالة الشحن والتسليم للطلب عبر GraphQL"""
        mutation = self._extract_query("ChangeFulfillmentStatus")
        if not mutation:
            return None
        try:
            variables = {
                "input": {
                    "orderId": str(qid),
                    "fulfillmentStatus": str(fulfillment_status)
                }
            }
            result = self.client.execute(mutation, variables, operation_name="ChangeFulfillmentStatus")
            return result.get('changeFulfillmentStatus') if result else None
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في تحديث حالة الشحن للطلب {qid}: {e}")
            return None

    def delete_order(self, qid: str) -> bool:
        mutation = self._extract_query("DeleteOrder")
        try:
            result = self.client.execute(mutation, {"id": qid}, operation_name="DeleteOrder")
            return result.get('deleteOrder', False) if result else False
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في حذف الطلب {qid}: {e}")
            return False
