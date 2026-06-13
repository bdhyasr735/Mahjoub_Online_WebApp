# coding: utf-8
# 📂 apps/utils/bridge_engine.py

import requests
import os
from config import Config

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
        # استخدام الحقل الصحيح المكتشف findAllProducts
        query = """
        query GetProducts($limit: Int) {
            findAllProducts(limit: $limit) {
                data {
                    title
                    price
                    quantity
                    status
                    image_url
                }
            }
        }
        """
        variables = {"limit": limit}
        data = self.execute_query(query, variables)
        
        # استخراج البيانات من المسار المكتشف
        return data.get('findAllProducts', {}).get('data', [])
