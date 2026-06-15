# 📂 apps/utils/orders_engine.py
from apps.extensions import db
from apps.models.order_db import Order
import requests
import logging

logger = logging.getLogger(__name__)

class OrdersEngine:
    def __init__(self):
        # رابط الـ API الخاص بـ قمرة
        self.api_url = "https://mahjoub.online/admin/graphql"
        # مفتاح الـ API مع صيغة Bearer المطلوبة للـ Authorization
        self.api_key = "qmr_e063f7f4-ed44-4c86-b105-8405326b9eb9"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}", 
            "Content-Type": "application/json"
        }

    def fetch_orders_from_qumra(self):
        print("DEBUG: بدء عملية استكشاف الـ Schema الحقيقية للحقول...")
        
        # استعلام Introspection لجلب تفاصيل حقول كائن Order
        # هذا سيخبرنا بالأسماء الدقيقة التي يتوقعها سيرفر قمرة
        payload = {
            "query": """
            query {
                __type(name: "Order") {
                    fields {
                        name
                        type {
                            name
                            kind
                        }
                    }
                }
            }
            """
        }
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers, timeout=15)
            result = response.json()
            
            # طباعة النتيجة في الـ Logs
            # بعد الضغط على المزامنة، ابحث عن هذا السطر في سجلات Render
            print(f"DEBUG: خريطة الحقول المتاحة (الرد الخام): {result}")
            
            return [] 
        except Exception as e:
            print(f"DEBUG: خطأ في الاستكشاف: {str(e)}")
            return []

    def sync_orders_to_db(self):
        print("DEBUG: بدء عملية المزامنة...")
        # تنفيذ عملية الاستكشاف فقط في هذه المرحلة
        self.fetch_orders_from_qumra()
        
        print("DEBUG: انتهت مرحلة الاستكشاف. يرجى مراجعة الـ Logs.")
