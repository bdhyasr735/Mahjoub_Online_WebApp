# coding: utf-8
# 📂 apps/utils/bridge_engine.py

import requests
import os

class QumraBridgeEngine:
    def __init__(self):
        self.endpoint = "https://mahjoub.online/admin/graphql"
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
            if response.status_code != 200:
                print(f"❌ DEBUG: Status {response.status_code} | Body: {response.text}")
                return {}
            
            result = response.json()
            if 'errors' in result:
                print(f"❌ GraphQL Errors: {result['errors']}")
                return {}
            return result.get('data', {})
        except Exception as e:
            print(f"⚠️ Connection Error: {e}")
            return {}

    def fetch_latest_products(self, limit=10):
        # استخدام الأسماء الصحيحة التي طلبها السيرفر
        query = """
        query {
            findAllProducts {
                data {
                    title
                    pricing
                    quantity
                    status
                    images
                }
            }
        }
        """
        data = self.execute_query(query)
        
        # استخراج البيانات
        products = data.get('findAllProducts', {}).get('data', [])
        
        # تحويل الحقول لتناسب القالب (لأن القالب يتوقع image_url وليس images)
        for p in products:
            # إذا كانت 'images' قائمة، نأخذ العنصر الأول، وإلا نتركها
            if isinstance(p.get('images'), list) and len(p['images']) > 0:
                p['image_url'] = p['images'][0]
            else:
                p['image_url'] = None
                
            # التعامل مع الحقول الأخرى إذا كانت تابعة لـ pricing
            if isinstance(p.get('pricing'), dict):
                p['price'] = p['pricing'].get('price', 0)
            else:
                p['price'] = p.get('pricing', 0)
                
        return products
