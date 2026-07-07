# coding: utf-8
# 📂 apps/services/graphql_client.py - النسخة النهائية والمحكمة

import requests
import logging
from config import Config

logger = logging.getLogger(__name__)

class QomrahGraphQLClient:
    """عميل متخصص لجلب بيانات الطلبات من منصة قمرة عبر GraphQL."""

    @staticmethod
    def _get_headers():
        """تحضير الترويسات الأمنية لتجاوز حماية CSRF ومتطلبات Apollo."""
        return {
            "Authorization": f"Bearer {Config.QUMRA_API_KEY}",
            "Content-Type": "application/json",
            "x-apollo-operation-name": "GetOrders",
            "apollo-require-preflight": "true"
        }

    @staticmethod
    def fetch_orders(headers=None):
        """جلب قائمة الطلبات مع معالجة الترويسات المطلوبة للاتصال الآمن."""
        
        # استخدام الترويسات الممررة أو الافتراضية
        current_headers = headers if headers is not None else QomrahGraphQLClient._get_headers()
        
        # الـ Query المحدث ليتطابق مع هيكلية البيانات المطلوبة من السيرفر
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
            # تنفيذ الطلب مع إضافة 'operationName' صراحة في الـ json payload
            # لضمان التطابق التام مع ترويسة x-apollo-operation-name
            payload = {
                'query': query,
                'operationName': 'GetOrders'
            }
            
            response = requests.post(
                Config.QUMRA_API_URL, 
                json=payload,
                headers=current_headers,
                timeout=15
            )
            
            # التحقق من نجاح الطلب وإثارة استثناء في حال وجود خطأ في السيرفر
            response.raise_for_status()
            result = response.json()
            
            # استخراج البيانات بدقة من الهيكل المتداخل للاستجابة
            data = result.get('data', {}).get('findAllOrders', {}).get('data', [])
            return data
            
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"❌ خطأ HTTP أثناء الاتصال بـ GraphQL: {http_err}")
            # طباعة نص الاستجابة من السيرفر يساعدنا في كشف أسباب الرفض الأمنية
            logger.error(f"Response Content: {response.text}")
            return []
        except Exception as e:
            logger.error(f"❌ خطأ غير متوقع في الاتصال بـ GraphQL: {e}")
            return []
