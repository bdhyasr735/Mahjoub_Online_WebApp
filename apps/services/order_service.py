# coding: utf-8
# 📂 apps/services/order_service.py

import os
from typing import Dict, Any, Optional, List
from .graphql_client import GraphQLClient
from datetime import datetime
from sqlalchemy import or_


class OrderService:
    """خدمة إدارة الطلبات والمزامنة"""
    
    def __init__(self, client: GraphQLClient):
        self.client = client
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.query_file_path = os.path.join(current_dir, 'orders_queries.graphql')
        
        try:
            with open(self.query_file_path, 'r', encoding='utf-8') as f:
                self.queries_content = f.read()
        except FileNotFoundError:
            print(f"⚠️ [OrderService]: لم يتم العثور على ملف الاستعلامات")
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

    def get_order(self, qid: str) -> Optional[Dict[str, Any]]:
        """جلب تفاصيل الطلب باستخدام المعرف qid"""
        query = self._extract_query("FindOrderById")
        try:
            result = self.client.execute(query, {"id": qid}, operation_name="FindOrderById")
            if result and 'findOrderById' in result:
                return result['findOrderById']
            return None
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في جلب الطلب {qid}: {e}")
            return None

    def get_all_orders(self, page: int = 1, per_page: int = 10, supplier_id: str = None, status: str = None, search: str = None, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """
        جلب قائمة الطلبات من قمرة ودمجها في قاعدة البيانات المحلية وربطها بالموردين.
        """
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
            pagination_data = {"totalItems": 0, "totalPages": 1, "currentPage": page, "limit": per_page, "hasNextPage": False}
            
            if result and 'findAllOrders' in result:
                orders_data = result['findAllOrders'].get('data', [])
                pagination_data = result['findAllOrders'].get('pagination', {})
                
                # حفظ الطلبات في قاعدة البيانات المحلية
                try:
                    from apps.models.orders_db import Order
                    from apps.models.order_items_db import OrderItem
                    from apps.models.product_supplier_map import ProductSupplierMapping
                    from apps.extensions import db
                    
                    for order in orders_data:
                        qid = order.get('_id')
                        if not qid:
                            continue

                        # تحديد المورد من أول منتج في الطلب
                        supplier_id_found = None
                        if order.get('items'):
                            first_item = order['items'][0]
                            prod_qid = first_item.get('productId')
                            if prod_qid:
                                mapping = ProductSupplierMapping.query.filter_by(product_qid=prod_qid).first()
                                if mapping:
                                    supplier_id_found = mapping.supplier_id

                        # حالة الطلب (نستخدم `status` مباشرة لأن الموديل يتوقع نصاً)
                        status_str = order.get('status', 'pending')
                        if isinstance(status_str, dict):
                            status_str = status_str.get('code', 'pending')

                        # البحث عن الطلب في قاعدة البيانات
                        existing_order = Order.query.filter_by(id=qid).first()
                        
                        if existing_order:
                            # تحديث البيانات
                            existing_order.supplier_id = supplier_id_found
                            existing_order.status = status_str
                            existing_order.total_price = order.get('totalPrice', 0.0)
                            
                            # حذف العناصر القديمة وإعادة إضافتها
                            OrderItem.query.filter_by(order_id=existing_order.id).delete()
                        else:
                            # إنشاء طلب جديد
                            existing_order = Order(
                                id=qid,
                                supplier_id=supplier_id_found,
                                status=status_str,
                                total_price=order.get('totalPrice', 0.0)
                            )
                            db.session.add(existing_order)
                            db.session.flush()

                        # إضافة العناصر الجديدة
                        for item in order.get('items', []):
                            new_item = OrderItem(
                                order_id=existing_order.id,
                                title=item.get('productData', {}).get('title', 'منتج غير معروف'),
                                qty=item.get('quantity', 1),
                                subtotal=item.get('price', 0.0) * item.get('quantity', 1),
                                sku=item.get('productData', {}).get('sku', ''),
                                price_per_unit=item.get('price', 0.0)
                            )
                            db.session.add(new_item)
                        
                        db.session.commit()
                        
                except Exception as db_err:
                    print(f"⚠️ [OrderService] خطأ أثناء حفظ الطلبات محلياً: {db_err}")
                    db.session.rollback()

            return {
                "data": orders_data,
                "pagination": pagination_data
            }
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في جلب الطلبات: {e}")
            return {"data": [], "pagination": {"totalItems": 0, "totalPages": 1, "currentPage": page, "limit": per_page, "hasNextPage": False}}

    # ✅ دالة جديدة لجلب الطلبات من قاعدة البيانات المحلية (لتستخدم في العرض)
    def get_local_orders(self, page: int = 1, per_page: int = 10, supplier_id: int = None, status: str = None, search: str = None, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """
        جلب الطلبات من قاعدة البيانات المحلية مع دعم الترقيم والفلترة.
        """
        from apps.models.orders_db import Order
        from apps.models.supplier_db import Supplier
        from apps.extensions import db

        query = db.session.query(Order)

        # 1. فلترة المورد (إذا كان معرفاً)
        if supplier_id is not None:
            query = query.filter(Order.supplier_id == supplier_id)

        # 2. فلترة الحالة
        if status:
            query = query.filter(Order.status == status)

        # 3. فلترة التاريخ
        if date_from:
            query = query.filter(Order.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
        if date_to:
            query = query.filter(Order.created_at <= datetime.strptime(date_to, '%Y-%m-%d'))

        # 4. البحث (في رقم الطلب أو معرف العرض)
        if search:
            query = query.filter(or_(
                Order.id.ilike(f'%{search}%'),
                Order.order_id_display.ilike(f'%{search}%')
            ))

        # حساب العدد الكلي
        total_items = query.count()
        total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 1

        # تطبيق الترقيم
        orders = query.order_by(Order.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

        # تحويل النتائج إلى قاموس مع إضافة اسم المورد
        orders_data = []
        for order in orders:
            order_dict = order.to_dict()
            # إضافة اسم المورد إذا وجد
            if order.supplier:
                order_dict['supplier_name'] = order.supplier.trade_name
            else:
                order_dict['supplier_name'] = 'غير مرتبط'
            # معالجة الحالة
            order_dict['status_text'] = order.status.title() if order.status else 'غير معروف'
            orders_data.append(order_dict)

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

    def create_order(self, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """إنشاء طلب جديد"""
        mutation = self._extract_query("CreateOrder")
        try:
            result = self.client.execute(mutation, {"input": input_data}, operation_name="CreateOrder")
            return result.get('createOrder') if result else None
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في إنشاء الطلب: {e}")
            return None

    def update_order_status(self, qid: str, status: str) -> Optional[Dict[str, Any]]:
        """تحديث حالة الطلب"""
        mutation = self._extract_query("UpdateOrderStatus")
        try:
            result = self.client.execute(mutation, {"id": qid, "status": status}, operation_name="UpdateOrderStatus")
            return result.get('updateOrderStatus') if result else None
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في تحديث حالة الطلب {qid}: {e}")
            return None

    def delete_order(self, qid: str) -> bool:
        """حذف طلب"""
        mutation = self._extract_query("DeleteOrder")
        try:
            result = self.client.execute(mutation, {"id": qid}, operation_name="DeleteOrder")
            return result.get('deleteOrder', False) if result else False
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في حذف الطلب {qid}: {e}")
            return None
