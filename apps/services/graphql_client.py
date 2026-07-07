# coding: utf-8
# 📂 apps/services/graphql_client.py - النسخة النهائية المتوافقة مع Qomrah Schema

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
        """جلب قائمة الطلبات باستخدام الدالة الصحيحة findAllOrders."""
        
        query = """
        query GetOrders($limit: Int, $offset: Int) {
          findAllOrders(limit: $limit, offset: $offset) {
            data {
              id
              customer_name
              total_price
              status
              created_at
            }
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
            
            # استخراج البيانات من المسار الصحيح: data -> findAllOrders -> data
            return result.get('data', {}).get('findAllOrders', {}).get('data', [])
            
        except Exception as e:
            logger.error(f"❌ خطأ أثناء جلب الطلبات: {e}")
            return []

    @staticmethod
    def get_order_details(order_id):
        """جلب تفاصيل طلب محدد باستخدام الدالة الصحيحة findOrderById."""
        
        query = """
        query GetOrder($id: ID!) {
          findOrderById(id: $id) {
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
            
            # استخراج البيانات من المسار: data -> findOrderById
            return result.get('data', {}).get('findOrderById')

        except Exception as e:
            logger.error(f"❌ خطأ في جلب تفاصيل الطلب {order_id}: {e}")
            return None
