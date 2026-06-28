# coding: utf-8
# 📂 apps/orders/services.py - منطق معالجة الطلبات والبيانات المالية

from apps.models.orders_db import Order, OrderFinancial
from apps.extensions import db
from sqlalchemy import or_

class OrderService:
    @staticmethod
    def get_paginated_orders(page=1, per_page=10, search_query=None, status=None):
        """
        جلب الطلبات مع بياناتها المالية مع دعم الفلترة والتقليب
        """
        # بناء الاستعلام الأساسي (Join بين الطلبات والبيانات المالية)
        query = db.session.query(Order, OrderFinancial).outerjoin(
            OrderFinancial, Order.id == OrderFinancial.order_id
        )

        # تطبيق فلاتر البحث
        if search_query:
            query = query.filter(
                or_(
                    Order._customer_name.ilike(f'%{search_query}%'), # بحث في الاسم المشفر (العمود الفعلي)
                    Order.order_id_display.ilike(f'%{search_query}%')
                )
            )

        # تطبيق فلترة الحالة (استخدام عمود status الفعلي في قاعدة البيانات)
        if status:
            query = query.filter(Order.status == status)

        # الترتيب حسب الأحدث
        query = query.order_by(Order.created_at.desc())

        # تنفيذ التقليب (Pagination)
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_order_with_financials(order_id):
        """
        جلب طلب محدد مع تفاصيله المالية
        """
        result = db.session.query(Order, OrderFinancial).outerjoin(
            OrderFinancial, Order.id == OrderFinancial.order_id
        ).filter(Order.id == order_id).first()
        
        return result

    @staticmethod
    def sync_all_orders():
        """
        خدمة استدعاء المزامنة
        """
        from apps.api.sync_engine import SyncEngine
        return SyncEngine.fetch_and_sync_order()
