# 📂 apps/api/sync_engine.py
import requests
import logging
from apps.extensions import db
from apps.models.orders_db import ProcessedOrder

logger = logging.getLogger(__name__)

class SyncEngine:
    """
    محرك المزامنة للاتصال المباشر بـ API سلة عند الحاجة (Manual/Scheduled Sync).
    """
    
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.salla.dev/admin/v2/orders"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def fetch_recent_orders(self):
        """جلب آخر الطلبات من سلة مباشرة"""
        try:
            response = requests.get(self.base_url, headers=self.headers)
            if response.status_code == 200:
                orders = response.json().get('data', [])
                self._process_and_save(orders)
                return len(orders)
            return 0
        except Exception as e:
            logger.error(f"❌ فشل الاتصال بسلة: {e}")
            return None

    def _process_and_save(self, orders):
        """معالجة وحفظ الطلبات (تجاوز المكرر)"""
        for order in orders:
            order_id = str(order['id'])
            # تحقق هل الطلب موجود في قاعدة البيانات المشفرة
            if not ProcessedOrder.query.get(order_id):
                new_order = ProcessedOrder(
                    id=order_id,
                    status=order.get('status', 'paid')
                )
                # استخدام الـ setter المشفر الخاص بك
                new_order.total_price = order.get('total', {}).get('amount', 0.0)
