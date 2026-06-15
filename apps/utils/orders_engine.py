# 📂 apps/utils/orders_engine.py
from flask import current_app
from apps.extensions import db
from apps.models.order_db import Order
import logging
import requests

logger = logging.getLogger(__name__)

class OrdersEngine:
    def __init__(self):
        self.api_url = current_app.config.get('QUMRA_API_URL', "https://mahjoub.online/admin/graphql")
        self.api_key = current_app.config.get('QUMRA_API_KEY')
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def fetch_orders_from_qumra(self):
        """كشف الهيكل الصحيح لـ API قمرة"""
        # هذا الاستعلام يطلب من السيرفر إعطاءنا أسماء الدوال المتاحة
        introspection_query = {
            "query": """
            query {
              __schema {
                queryType {
                  fields {
                    name
                  }
                }
              }
            }
            """
        }
        
        try:
            response = requests.post(self.api_url, json=introspection_query, headers=self.headers)
            if response.status_code == 200:
                # سنقوم بطباعة أسماء الدوال المتاحة في السجلات
                logger.info(f"إكتشاف الدوال المتاحة: {response.text}")
                return [] 
            else:
                logger.error(f"خطأ استكشاف: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"خطأ أثناء الاستكشاف: {str(e)}")
            return []

    def sync_orders_to_db(self):
        """مزامنة الطلبات"""
        raw_orders = self.fetch_orders_from_qumra()
        
        if not raw_orders:
            logger.warning("تمت عملية الاستكشاف. يرجى مراجعة السجلات أعلاه لمعرفة اسم الدالة الصحيح.")
            return
