# coding: utf-8
# 📂 apps/api/sync_engine.py - نسخة محدثة لاستقبال البيانات من المتصفح

import logging
from decimal import Decimal, InvalidOperation
from apps.extensions import db
from apps.models.orders_db import Order
from apps.models.financials_db import OrderFinancial
from apps.models.order_items_db import OrderItem
from apps.models.supplier_db import Supplier

logger = logging.getLogger(__name__)

class SyncEngine:
    
    @staticmethod
    def process_incoming_orders(orders_data):
        """
        دالة جديدة لاستقبال البيانات القادمة من المتصفح ومعالجتها.
        لم تعد هذه الدالة تتصل بـ QomrahGraphQLClient مباشرة.
        """
        if not orders_data:
            logger.warning("⚠️ لم يتم استلام أي بيانات للمزامنة.")
            return 0
            
        total_synced = 0
        for order_data in orders_data:
            if SyncEngine.process_financials(order_data):
                total_synced += 1
                
        logger.info(f"✅ تمت المعالجة بنجاح. إجمالي الطلبات المحدثة: {total_synced}")
        return total_synced

    @staticmethod
    def process_financials(order_data):
        """معالجة مالية مع تصحيح أسماء الحقول بناءً على Schema قمرة"""
        order_id = str(order_data.get('_id'))
        
        supplier_id = order_data.get('supplier_id')
        if not supplier_id:
            tracking_tag = order_data.get('tracking_tag')
            supplier = Supplier.query.filter_by(store_tag=tracking_tag).first()
            if supplier:
                supplier_id = supplier.id
            else:
                logger.error(f"❌ تعذر تحديد المورد للطلب {order_id}")
                return False

        try:
            total_price = Decimal(str(order_data.get('totalPrice', 0)))
        except (InvalidOperation, ValueError, TypeError):
            total_price = Decimal('0')
            
        items = order_data.get('items', [])

        try:
            order = Order.query.get(order_id)
            if not order:
                order = Order(
                    id=order_id,
                    order_id_display=f"Q-{order_id[-6:]}",
                    customer_name=order_data.get('customerName', 'عميل غير معروف'),
                    supplier_id=supplier_id,
                    total_price=float(total_price),
                    status='pending'
                )
                db.session.add(order)
                db.session.flush()

            # تحديث عناصر الطلب
            OrderItem.query.filter_by(order_id=order_id).delete()
            for item in items:
                new_item = OrderItem(
                    order_id=order_id,
                    title=item.get('productName', 'منتج غير معرف'),
                    qty=item.get('quantity', 1),
                    subtotal=Decimal(str(item.get('price', 0))),
                    sku=item.get('sku', 'N/A')
                )
                db.session.add(new_item)

            # التحديث المالي
            financial_record = OrderFinancial.query.filter_by(order_id=order_id).first()
            if not financial_record:
                financial_record = OrderFinancial(order_id=order_id, supplier_id=supplier_id)
            
            financial_record.total_paid = float(total_price)
            financial_record.mahjoub_commission = float(total_price * Decimal('0.20'))
            financial_record.supplier_cost = float(total_price * Decimal('0.80'))
            
            db.session.add(financial_record)
            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ خطأ حرج في معالجة الطلب {order_id}: {e}")
            return False
