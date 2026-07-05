# coding: utf-8
# 📂 apps/api/sync_engine.py - محرك المزامنة المحاسبي المحدث (نسخة المصنع)

import os
import logging
from decimal import Decimal
from apps.extensions import db
from apps.models.wallet_db import WalletTransaction, SupplierWallet
from apps.api.tracker_service import TrackerService

logger = logging.getLogger(__name__)

class SyncEngine:
    API_URL = "https://mahjoub.online/admin/graphql"  

    @staticmethod
    def _get_headers():
        api_key = os.environ.get("QUMRA_API_KEY", "qmr_e063f7f4-ed44-4c86-b105-8405326b9eb9")
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @staticmethod
    def process_financials(order_id, supplier_id, total_price, tracking_tag=None, product_currency='SAR'):
        """توزيع مالي ذكي للحصص مع دعم العملات المتعددة والربط المحاسبي"""
        try:
            total_price = Decimal(str(total_price))
            
            # 1. فك تشفير بيانات المسوق
            marketer_id = None
            if tracking_tag and '|' in tracking_tag:
                parts = tracking_tag.split('|')
                if len(parts) >= 2:
                    data = TrackerService.verify_and_resolve(parts[0], parts[1])
                    if data: marketer_id = data.get('marketer_id')

            # 2. جلب المحفظة
            wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
            if not wallet: return False

            # 3. منطق الحسابات (يتم دائماً بناءً على القيمة الواصلة من قمرة بالريال)
            supplier_cost = total_price * Decimal('0.80')
            platform_profit = total_price * Decimal('0.20')
            
            # خصم حصة المسوق (تُسجل دائماً بالريال كعملة المنصة الموحدة)
            if marketer_id:
                marketer_share = platform_profit * Decimal('0.50')
                platform_profit -= marketer_share
                db.session.add(WalletTransaction(
                    wallet_id=wallet.id, 
                    amount=marketer_share, 
                    trans_type='adjustment_debit',
                    currency='SAR',
                    description=f"عمولة مسوق للطلب {order_id}",
                    voucher_number=f"MKT-{order_id}",
                    reference_number=order_id
                ))

            # 4. تسجيل إيراد المبيعات للمورد (دائن) بالعملة الأصلية للمنتج
            db.session.add(WalletTransaction(
                wallet_id=wallet.id, 
                amount=supplier_cost, 
                trans_type='sale_revenue',
                currency=product_currency, # هنا يتم توجيه المبلغ للرصيد الصحيح (USD/YER/SAR)
                description=f"إيراد مبيعات الطلب {order_id} (عملة: {product_currency})",
                voucher_number=f"SUP-{order_id}",
                reference_number=order_id
            ))
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ خطأ في التوزيع المالي للطلب {order_id}: {e}")
            return False

    @staticmethod
    def fetch_and_sync_order():
        """هيكل تجريبي للزرع في المصنع"""
        # مثال لزراعة المنتجات الثلاثة برمجياً:
        test_orders = [
            {'id': 'T-USD-001', 's_id': 1, 'price': 100, 'curr': 'USD'},
            {'id': 'T-YER-002', 's_id': 1, 'price': 100, 'curr': 'YER'},
            {'id': 'T-SAR-003', 's_id': 1, 'price': 100, 'curr': 'SAR'}
        ]
        for o in test_orders:
            SyncEngine.process_financials(o['id'], o['s_id'], o['price'], product_currency=o['curr'])
        return True
