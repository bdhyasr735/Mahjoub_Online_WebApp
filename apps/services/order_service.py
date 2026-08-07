# coding: utf-8
# 📂 apps/services/order_service.py

import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, time
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
        """دالة مساعدة مجمعة لحفظ وتحديث الطلبات وعناصرها مع دعم تعدد الموردين المحليين وصور المنتجات"""
        try:
            from apps.models.orders_db import Order
            from apps.models.order_items_db import OrderItem
            from apps.models.product_supplier_map import ProductSupplierMapping
            from apps.extensions import db

            for order in orders_data:
                try:
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

                    # استخراج اسم العميل بشكل آمن
                    account_outer = order.get('account') or {}
                    account_inner = account_outer.get('account') or {}
                    raw_fullname = account_inner.get('fullname')

                    if raw_fullname and str(raw_fullname).strip():
                        customer_name = str(raw_fullname)
                    else:
                        customer_name = 'زائر' if order.get('type') == 'guest' else 'عميل غير معروف'

                    is_paid = bool(order.get('isPaid', False))
                    total_amount = float(order.get('totalPrice', 0.0) or 0.0)

                    created_at_str = order.get('createdAt')
                    created_at = datetime.now(timezone.utc).replace(tzinfo=None)
                    if created_at_str:
                        try:
                            clean_date_str = str(created_at_str).replace('Z', '').split('+')[0]
                            created_at = datetime.fromisoformat(clean_date_str)
                        except Exception:
                            pass

                    existing_order = db.session.get(Order, qid)

                    if existing_order:
                        existing_order.status_code = status_code
                        existing_order.status_title = status_title
                        existing_order.customer_name = customer_name
                        existing_order.is_paid = is_paid
                        existing_order.total_amount = total_amount
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
                            total_amount=total_amount,
                            created_at=created_at
                        )
                        db.session.add(existing_order)
                        db.session.flush()

                    primary_supplier_id = None
                    for item in items_list:
                        if not item:
                            continue
                        
                        # استخراج بيانات المنتج من productData بدقة
                        prod_data = item.get('productData') or {}
                        qty = int(item.get('quantity', 1) or 1)
                        price = float(item.get('price', 0.0) or (prod_data.get('price') or 0.0))
                        prod_id = item.get('productId', '')
                        safe_prod_id = str(prod_id) if prod_id is not None else ""

                        # ⚡️ سحب الاسم الحقيقي بجميع الاحتمالات الممكنة
                        product_name = "منتج غير معروف"
                        if isinstance(prod_data, dict):
                            product_name = prod_data.get('title') or prod_data.get('name') or prod_data.get('productName')
                        
                        if not product_name:
                            product_name = item.get('title') or item.get('product_name')

                        if not product_name:
                            product_name = f"منتج ({safe_prod_id[:8]})" if safe_prod_id else "منتج بدون اسم"

                        # 🖼️ استخراج رابط صورة المنتج بدقة
                        prod_image = ""
                        if isinstance(prod_data, dict):
                            image_obj = prod_data.get('image') or prod_data.get('img')
                            if isinstance(image_obj, dict):
                                prod_image = image_obj.get('fileUrl') or image_obj.get('url') or image_obj.get('path') or ''
                            elif isinstance(image_obj, str):
                                prod_image = image_obj
                        
                        if not prod_image and item.get('product_image'):
                            prod_image = item.get('product_image')

                        # البحث عن المورد المحلي
                        item_supplier_id = None
                        if safe_prod_id:
                            try:
                                mapping = ProductSupplierMapping.query.filter_by(product_qid=safe_prod_id).first()
                                if mapping:
                                    item_supplier_id = mapping.supplier_id
                            except Exception:
                                pass

                        if primary_supplier_id is None and item_supplier_id is not None:
                            primary_supplier_id = item_supplier_id

                        new_item = OrderItem(
                            order_id=existing_order.id,
                            supplier_id=item_supplier_id,
                            product_name=product_name,
                            product_image=prod_image,
                            quantity=qty,
                            price=price
                        )
                        db.session.add(new_item)

                    if hasattr(existing_order, 'supplier_id'):
                        existing_order.supplier_id = primary_supplier_id

                    db.session.commit()
                
                except Exception as order_err:
                    db.session.rollback()
                    print(f"⚠️ [OrderService] فشل حفظ الطلب وتم تخطيه: {order_err}")

        except Exception as db_err:
            print(f"⚠️ [OrderService] خطأ تفصيلي أثناء حفظ الطلبات محلياً: {db_err}")
            db.session.rollback()

    def get_order(self, qid: str) -> Optional[Dict[str, Any]]:
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
        from apps.models.orders_db import Order
        from apps.extensions import db

        order_data = self.get_order(qid)
        if order_data:
            self._save_orders_to_db([order_data])

        return db.session.get(Order, qid)

    def get_order_by_id(self, qid: str):
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
        # إرسال المتغيرات بشكل آمن أو بدونها بناءً على تصميم السيرفر
        variables = {"page": page, "limit": per_page}

        query = self._extract_query("FindAllOrders")
        try:
            result = self.client.execute(query, variables, operation_name="FindAllOrders")

            orders_data = []
            pagination_data = {
                "totalItems": 0, "totalPages": 1, "currentPage": page, "limit": per_page, "hasNextPage": False
            }

            if result and isinstance(result, dict) and 'findAllOrders' in result and result['findAllOrders']:
                res_content = result['findAllOrders']
                if isinstance(res_content, dict):
                    orders_data = res_content.get('data', []) or []
                    pagination_data = res_content.get('pagination', {}) or {}
                elif isinstance(res_content, list):
                    orders_data = res_content
                
                self._save_orders_to_db(orders_data)

            return {"data": orders_data, "pagination": pagination_data}
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في جلب الطلبات: {e}")
            import traceback
            traceback.print_exc()
            return {"data": [], "pagination": {"totalItems": 0, "totalPages": 1, "currentPage": page, "limit": per_page, "hasNextPage": False}}

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
        from apps.models.orders_db import Order
        from apps.models.order_items_db import OrderItem
        from apps.extensions import db

        try:
            query = db.session.query(Order)

            if supplier_id is not None:
                query = query.filter(
                    or_(
                        Order.supplier_id == supplier_id if hasattr(Order, 'supplier_id') else False,
                        Order.items.any(OrderItem.supplier_id == supplier_id)
                    )
                )
            if status:
                query = query.filter(Order.status_code == status)
                
            if date_from:
                query = query.filter(Order.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
            if date_to:
                dt_to = datetime.combine(datetime.strptime(date_to, '%Y-%m-%d').date(), time.max)
                query = query.filter(Order.created_at <= dt_to)
                
            if search:
                query = query.filter(or_(
                    Order.id.ilike(f'%{search}%'),
                    Order.customer_name.ilike(f'%{search}%')
                ))

            total_items = query.count()
            total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 1

            orders = query.order_by(Order.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

            orders_data = []
            for order in orders:
                try:
                    if hasattr(order, 'to_dict'):
                        order_dict = order.to_dict()
                    else:
                        order_dict = {
                            'id': order.id,
                            'customer_name': order.customer_name,
                            'status_code': order.status_code,
                            'status_title': order.status_title,
                            'is_paid': order.is_paid,
                            'total_amount': getattr(order, 'total_amount', 0.0),
                            'total_price': getattr(order, 'total_amount', 0.0),
                            'created_at': order.created_at.isoformat() if order.created_at else None
                        }
                    
                    if hasattr(order, 'supplier') and order.supplier:
                        order_dict['supplier_name'] = order.supplier.name
                    else:
                        order_dict['supplier_name'] = 'غير مرتبط'
                        
                    orders_data.append(order_dict)
                except Exception as ser_err:
                    print(f"⚠️ [OrderService] فشل تحويل الطلب إلى JSON: {ser_err}")
                    continue

            return {
                'data': orders_data,
                'pagination': {
                    'totalItems': total_items, 'totalPages': total_pages,
                    'currentPage': page, 'limit': per_page, 'hasNextPage': page < total_pages
                }
            }
        except Exception as e:
            print(f"❌ [OrderService] خطأ حرج أثناء جلب الطلبات المحلية: {e}")
            return {
                'data': [],
                'pagination': {'totalItems': 0, 'totalPages': 1, 'currentPage': page, 'limit': per_page, 'hasNextPage': False}
            }

    def delete_order(self, qid: str) -> bool:
        mutation = self._extract_query("DeleteOrder")
        try:
            result = self.client.execute(mutation, {"id": qid}, operation_name="DeleteOrder")
            return result.get('deleteOrder', False) if result else False
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في حذف الطلب {qid}: {e}")
            return False