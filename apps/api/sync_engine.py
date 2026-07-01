# coding: utf-8
# 📂 apps/api/sync_engine.py - محرك المزامنة المحدث

import os
import requests
import logging
from apps.extensions import db
from apps.models.sync_log import SyncLog
from apps.models.wallet_db import WalletTransaction
from apps.supplier_wallet.services import WalletService

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
    def fetch_and_sync_order():
        """دالة سحب الطلبات ومعالجتها مالياً"""
        logger.info("🚀 محاولة سحب الطلبات مباشرة...")
        
        # استعلام GraphQL محدث ليشمل supplierId
        query = """
        query {
            findAllOrders {
                id
                totalPrice
                status
                supplierId
            }
        }
        """
        
        try:
            response = requests.post(
                SyncEngine.API_URL, 
                json={'query': query}, 
                headers=SyncEngine._get_headers(), 
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json().get('data', {}).get('findAllOrders', [])
                
                for order in data:
                    # 1. فلترة الطلبات المكتملة فقط
                    if order.get('status') == 'DELIVERED':
                        # 2. منع التكرار: التأكد أن الطلب لم تتم تسويته سابقاً
                        ref_num = f"QMR-{order['id']}"
                        exists = WalletTransaction.query.filter_by(reference_number=ref_num).first()
                        
                        if not exists and order.get('supplierId'):
                            WalletService.sync_order_payment(
                                supplier_id=order['supplierId'],
                                order_id=order['id'],
                                amount=order['totalPrice'],
                                currency='SAR'
                            )
                            logger.info(f"✅ تمت تسوية الطلب {order['id']} مالياً.")
                
                SyncEngine._log_sync('orders', 'success', "تم سحب ومعالجة الطلبات بنجاح.")
                return True
            else:
                error_msg = f"فشل السحب: {response.status_code} - {response.text}"
                logger.error(f"❌ {error_msg}")
                SyncEngine._log_sync('orders', 'failed', error_msg)
                return False
                
        except Exception as e:
            err_str = str(e)
            logger.error(f"❌ خطأ فني أثناء السحب: {err_str}")
            SyncEngine._log_sync('orders', 'failed', err_str)
            return False

    @staticmethod
    def _log_sync(sync_type, status, message):
        """تسجيل العمليات في قاعدة البيانات"""
        try:
            log = SyncLog(sync_type=sync_type, status=status, error_message=message)
            db.session.add(log)
            db.session.commit()
        except Exception:
            db.session.rollback()
