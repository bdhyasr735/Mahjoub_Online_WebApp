# coding: utf-8
# 📂 apps/services/graphql_client.py - النسخة النهائية المحدثة

import requests
import logging
from config import Config

logger = logging.getLogger(__name__)

class QomrahGraphQLClient:
    """عميل متخصص لجلب بيانات الطلبات من منصة قمرة عبر GraphQL."""

    @staticmethod
    def _get_headers():
        """تحضير الترويسات الأمنية لتجاوز CSRF."""
        return {
            "Authorization": f"Bearer {Config.QUMRA_API_KEY}",
            "Content-Type": "application/json",
            "x-apollo-operation-name": "GetOrders",
            "apollo-require-preflight": "true"
        }

    @staticmethod
    def fetch_orders(headers=None):
        """جلب قائمة الطلبات. تم إضافة headers كمعامل اختياري لحل الخطأ."""
        
        # استخدام الترويسات الممررة أو الافتراضية
        current_headers = headers if headers is not None else QomrahGraphQLClient._get_headers()
        
        query = """
        query GetOrders {
          findAllOrders { 
            data {
              _id
              totalPrice
              status {
                name
              }
              createdAt
              items {
                productName
                quantity
                price
                sku
              }
            }
          }
        }
        """
        
        try:
            response = requests.post(
                Config.QUMRA_API_URL, 
                json={'query': query},
                headers=current_headers,
                timeout=15
            )
            response.raise_for_status()
            result = response.json()
            
            return result.get('data', {}).get('findAllOrders', {}).get('data', [])
            
        except Exception as e:
            logger.error(f"❌ خطأ في الاتصال بـ GraphQL: {e}")
            return []
