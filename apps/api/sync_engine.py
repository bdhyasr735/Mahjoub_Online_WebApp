# coding: utf-8
# 📂 apps/api/sync_engine.py - محرك المزامنة المحاسبي (النسخة النهائية)

import logging
from decimal import Decimal
from apps.extensions import db
from apps.models.wallet_db import WalletTransaction, SupplierWallet
from apps.models.sync_log import SyncLog 
from apps.models.financials_db import OrderFinancial
from apps.models.order_items_db import OrderItem
from apps.api.tracker_service import TrackerService

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
        """
        معالجة مالية شاملة للطلب القادم من Qumra/GraphQL
        order_data: قاموس يحتوي على تفاصيل الطلب والمنتجات
        """
        order_id = str(order_data.get('id'))
        supplier_id = order_data.get('supplier_id')
        total_price = Decimal(str(order_data.get('total_price', 0)))
        tracking_tag = order_data.get('tracking_tag')
        product_currency = order_data.get('currency', 'SAR')
        items = order_data.get('items', [])

        try:
            # 1. التحقق من وجود محفظة للمورد
            wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
            if not wallet:
                raise Exception(f"لا توجد محفظة نشطة للمورد ID: {supplier_id}")

            # 2. تسجيل المنتجات (OrderItem)
            for item in items:
                new_item = OrderItem(
                    order_id=order_id,
                    title=item.get('title'),
                    qty=item.get('qty', 1),
                    subtotal=Decimal(str(item.get('subtotal', 0))),
                    sku=item.get('sku')
                )
                db.session.add(new_item)

            # 3. فك تشفير المسوق (إن وجد)
            marketer_id = None
            if tracking_tag and '|' in tracking_tag:
                parts = tracking_tag.split('|')
                if len(parts) >= 2:
                    data = TrackerService.verify_and_resolve(parts[0], parts[1])
                    if data: marketer_id = data.get('marketer_id')

            # 4. توزيع الحصص المالية
            supplier_cost = total_price * Decimal('0.80')
            platform_profit = total_price * Decimal('0.20')
            
            # خصم عمولة المسوق من حصة المنصة
            if marketer_id:
                marketer_share = platform_profit * Decimal('0.50')
                platform_profit -= marketer_share
                db.session.add(WalletTransaction(
                    wallet_id=wallet.id, amount=marketer_share, 
                    trans_type='adjustment_debit', currency='SAR',
                    description=f"عمولة مسوق للطلب {order_id}",
                    voucher_number=f"MKT-{order_id}", reference_number=order_id
                ))

            # 5. تسجيل إيراد المورد في المحفظة
            db.session.add(WalletTransaction(
                wallet_id=wallet.id, amount=supplier_cost,
                trans_type='sale_revenue', currency=product_currency,
                description=f"إيراد مبيعات الطلب {order_id}",
                voucher_number=f"SUP-{order_id}", reference_number=order_id
            ))

            # 6. التوثيق في المركز المالي (OrderFinancial)
            financial_record = OrderFinancial(
                order_id=order_id,
                supplier_id=supplier_id,
                currency=product_currency,
                total_paid=float(total_price),
                mahjoub_commission=float(platform_profit),
                supplier_cost=float(supplier_cost),
                settlement_status='pending'
            )
            db.session.add(financial_record)
            
            # اعتماد العملية ككل (Atomic Transaction)
            db.session.commit()
            
            SyncEngine._log_to_db(order_id, supplier_id, 'financial_sync', 'success')
            return True

        except Exception as e:
            db.session.rollback()
            SyncEngine._log_to_db(order_id, supplier_id, 'financial_sync', 'failed', error=str(e))
            logger.error(f"❌ خطأ حرج في معالجة الطلب {order_id}: {e}")
            return False
