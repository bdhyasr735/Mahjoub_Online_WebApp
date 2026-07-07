# coding: utf-8
# 📂 apps/services/graphql_client.py - عميل الاتصال بـ Qumra GraphQL

import requests
import logging
from config import Config

logger = logging.getLogger(__name__)

class QomrahGraphQLClient:
    """عميل متخصص لجلب بيانات الطلبات من منصة قمرة عبر GraphQL."""

    @staticmethod
    def get_order_details(order_id):
        query = """
        query GetOrder($id: ID!) {
            order(id: $id) {
                id
                supplier_id
                total_price
                tracking_tag
                currency
                items {
                    title
                    qty
                    subtotal
                    sku
                }
            }
        }
        """
        
        headers = {
            "Authorization": f"Bearer {Config.QUMRA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                Config.QUMRA_API_URL, 
                json={'query': query, 'variables': {'id': order_id}},
                headers=headers,
                timeout=10 # إضافة وقت انتظار لضمان عدم تعليق السيرفر
            )
            
            # التحقق من أن الاستجابة ناجحة (HTTP 200)
            response.raise_for_status()
            
            result = response.json()
            
            # التحقق من وجود أخطاء في الـ GraphQL نفسه
            if 'errors' in result:
                logger.error(f"❌ خطأ GraphQL في جلب الطلب {order_id}: {result['errors']}")
                return None
                
            return result.get('data', {}).get('order')

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ خطأ في الاتصال بسيرفر قمرة عند جلب الطلب {order_id}: {e}")
            return None
