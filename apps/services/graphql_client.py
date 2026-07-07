# coding: utf-8
# 📂 apps/services/graphql_client.py - النسخة المصححة للاتصال بـ GraphQL

import requests
import logging
from config import Config

logger = logging.getLogger(__name__)

class QomrahGraphQLClient:
    """عميل متخصص لجلب بيانات الطلبات من منصة قمرة عبر GraphQL."""

    @staticmethod
    def _get_headers():
        return {
            "Authorization": f"Bearer {Config.QUMRA_API_KEY}",
            "Content-Type": "application/json"
        }

    @staticmethod
    def fetch_orders(limit=20, offset=0):
        """جلب قائمة الطلبات باستخدام استعلام GraphQL قياسي."""
        
        # استعلام GraphQL الصحيح (يجب مراجعة أسماء الحقول في Sandbox الخاص بك)
        query = """
        query GetOrders($limit: Int, $offset: Int) {
            orders(limit: $limit, offset: $offset) {
                id
                customer_name
                total_price
                status
                created_at
            }
        }
        """
        variables = {"limit": limit, "offset": offset}
        
        try:
            response = requests.post(
                Config.QUMRA_API_URL, 
                json={'query': query, 'variables': variables},
                headers=QomrahGraphQLClient._get_headers(),
                timeout=15
            )
            response.raise_for_status()
            result = response.json()
            
            # استخراج البيانات من الهيكل القياسي للرد
            return result.get('data', {}).get('orders', [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ خطأ في الاتصال بـ GraphQL: {e}")
            return []

    @staticmethod
    def get_order_details(order_id):
        """جلب تفاصيل طلب محدد عبر GraphQL."""
        
        query = """
        query GetOrder($id: ID!) {
            order(id: $id) {
                id
                customer_name
                total_price
                status
            }
        }
        """
        variables = {"id": order_id}
        
        try:
            response = requests.post(
                Config.QUMRA_API_URL, 
                json={'query': query, 'variables': variables},
                headers=QomrahGraphQLClient._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            return result.get('data', {}).get('order')

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ خطأ في جلب تفاصيل الطلب {order_id}: {e}")
            return None
