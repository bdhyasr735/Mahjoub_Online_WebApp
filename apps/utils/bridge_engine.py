# coding: utf-8
# 📂 apps/utils/bridge_engine.py

import requests
import os
from config import Config

class QumraBridgeEngine:
    def __init__(self):
        self.endpoint = "https://mahjoub.online/admin/graphql"
        # التأكد من جلب المفتاح من متغيرات البيئة بوضوح
        api_token = os.environ.get('QUMRA_API_KEY', '').strip()
        
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def execute_query(self, query, variables=None):
        payload = {"query": query, "variables": variables or {}}
        try:
            response = requests.post(self.endpoint, json=payload, headers=self.headers, timeout=15)
            
            # تسجيل تفاصيل الخطأ في حال حدوثه لتسهيل الإصلاح
            if response.status_code != 200:
                print(f"❌ DEBUG: Status {response.status_code} | Body: {response.text}")
                return {}
            
            result = response.json()
            
            # فحص وجود أخطاء داخل استجابة GraphQL نفسها (أحياناً تكون 200 ولكن هناك أخطاء برمجية)
            if 'errors' in result:
                print(f"❌ GraphQL Errors: {result['errors']}")
                return {}
                
            return result.get('data', {})
            
        except Exception as e:
            print(f"⚠️ Connection Error: {e}")
            return {}

    def fetch_latest_products(self, limit=10):
        # استعلام GraphQL - تأكد أن الحقول (title, _id) مطابقة للموجود في السيرفر
        query = """
        query GetProducts($first: Int) {
            products(first: $first) {
                data {
                    title
                    _id
                }
            }
        }
        """
        variables = {"first": limit}
        data = self.execute_query(query, variables)
        
        # استخراج البيانات من المسار المكتشف
        return data.get('products', {}).get('data', [])
