# coding: utf-8
# 📂 apps/api/sync_engine.py - محرك المزامنة المصحح للمنتجات غير المرتبطة

import logging
from decimal import Decimal, InvalidOperation
from apps.extensions import db
from apps.models.orders_db import Order
from apps.models.wallet_db import WalletTransaction, SupplierWallet
from apps.models.sync_log import SyncLog 
from apps.models.financials_db import OrderFinancial
from apps.models.order_items_db import OrderItem

logger = logging.getLogger(__name__)

class SyncEngine:
    @staticmethod
    def _log_to_db(order_id, supplier_id, sync_type, status, error=None):
        try:
            log = SyncLog(
                supplier_id=supplier_id,
                order_id=order_id,
                sync_type=sync_type,
                status=status,
                error_message=str(error) if error else None
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            logger.error(f"فشل في تسجيل السجل: {e}")

    @staticmethod
    def process_financials(order_data):
        """معالجة مالية شاملة للطلب (تتعامل مع البيانات حتى لو كانت غير مرتبطة سابقاً)"""
        order_id = str(order_data.get('id'))
        supplier_id = order_data.get('supplier_id')
        
        # حماية من تحويل القيم الفارغة
        try:
            total_price = Decimal(str(order_data.get('total_price', 0)))
        except InvalidOperation:
            total_price = Decimal('0')
            
        product_currency = order_data.get('currency', 'SAR')
        items = order_data.get('items', [])

        try:
            # 1. التأكد من وجود سجل الطلب (إنشاء جديد إذا لم يوجد)
            order = Order.query.get(order_id)
            if not order:
                order = Order(
                    id=order_id,
                    order_id_display=f"Q-{order_id[-6:]}",
                    customer_name=order_data.get('customer_name', 'عميل غير معروف'),
                    supplier_id=supplier_id,
                    total_price=float(total_price),
                    status='pending'
                )
                db.session.add(order)
                db.session.flush() # تفعيل الـ ID للربط

            # 2. تسجيل المنتجات (بدون اشتراط ارتباط مسبق)
            # نقوم بمسح أي منتجات مرتبطة سابقاً بنفس الـ order_id لتجنب التكرار عند إعادة المزامنة
            OrderItem.query.filter_by(order_id=order_id).delete()
            
            for item in items:
                new_item = OrderItem(
                    order_id=order_id,
                    title=item.get('title', 'منتج غير معرف'),
                    qty=item.get('qty', 1),
                    subtotal=Decimal(str(item.get('subtotal', 0))),
                    sku=item.get('sku', 'N/A') # التعامل مع غياب الـ SKU
                )
                db.session.add(new_item)

            # 3. التحقق من وجود محفظة المورد
            wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
            if not wallet:
                # لتفادي توقف النظام، نقوم بإنشاء سجل مالي معلق حتى يتم ربط المحفظة لاحقاً
                logger.warning(f"تحذير: لا توجد محفظة للمورد {supplier_id}، سيتم تعليق المعالجة المالية.")
            else:
                # تسجيل إيراد المورد
                supplier_cost = total_price * Decimal('0.80')
                db.session.add(WalletTransaction(
                    wallet_id=wallet.id, amount=supplier_cost,
                    trans_type='sale_revenue', currency=product_currency,
                    description=f"إيراد مبيعات الطلب {order_id}",
                    reference_number=order_id
                ))

            # 4. التوثيق في المركز المالي (OrderFinancial)
            # استخدام merge لتحديث السجل إذا كان موجوداً مسبقاً
            financial_record = OrderFinancial.query.filter_by(order_id=order_id).first()
            if not financial_record:
                financial_record = OrderFinancial(order_id=order_id, supplier_id=supplier_id)
            
            financial_record.currency = product_currency
            financial_record.total_paid = float(total_price)
            financial_record.mahjoub_commission = float(total_price * Decimal('0.20'))
            financial_record.supplier_cost = float(total_price * Decimal('0.80'))
            financial_record.settlement_status = 'pending'
            
            db.session.add(financial_record)
            
            db.session.commit()
            SyncEngine._log_to_db(order_id, supplier_id, 'financial_sync', 'success')
            return True

        except Exception as e:
            db.session.rollback()
            SyncEngine._log_to_db(order_id, supplier_id, 'financial_sync', 'failed', error=str(e))
            logger.error(f"❌ خطأ حرج في معالجة الطلب {order_id}: {e}")
            return False
