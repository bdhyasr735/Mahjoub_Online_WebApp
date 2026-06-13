# coding: utf-8
# 📂 apps/utils/bridge_engine.py

import requests
from config import Config

class QumraBridgeEngine:
    def __init__(self):
        self.endpoint = "https://mahjoub.online/admin/graphql"
        api_token = getattr(Config, 'QUMRA_API_KEY', '').strip()
        
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": "https://mahjoub.online",
            "Referer": "https://mahjoub.online/admin/"
        }

    def execute_query(self, query, variables=None):
        payload = {"query": query, "variables": variables or {}}
        try:
            response = requests.post(self.endpoint, json=payload, headers=self.headers, timeout=15)
            if response.status_code != 200:
                print(f"DEBUG: Status {response.status_code} | Response: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            
            if 'errors' in result:
                print(f"⚠️ GraphQL Errors: {result['errors']}")
            return result.get('data', {})
        except Exception as e:
            print(f"⚠️ Connection Error: {e}")
            return {}

    def fetch_latest_products(self, limit=10, page=1, search_term=None):
        # الاستعلام الأعمى: طلب الحقول الأساسية فقط للتأكد من نجاح الاتصال
        # تمت إزالة 'input' وإزالة الحقول المعقدة لتشخيص المشكلة
        query = """
        query GetProducts($limit: Int, $page: Int) {
            findAllProducts(limit: $limit, page: $page) {
                data {
                    title
                    quantity
                }
            }
        }
        """
        variables = {"limit": limit, "page": page}
        data = self.execute_query(query, variables)
        
        products = data.get('findAllProducts', {}).get('data', [])
        
        return products if isinstance(products, list) else []
