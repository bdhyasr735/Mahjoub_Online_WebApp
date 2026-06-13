# coding: utf-8
import requests
from config import Config

class QumraBridgeEngine:
    def __init__(self):
        self.endpoint = "https://mahjoub.online/admin/graphql"
        api_key = getattr(Config, 'QUMRA_API_KEY', '') or ""
        self.headers = {
            "x-api-key": str(api_key).strip(), 
            "Content-Type": "application/json"
        }

    def execute_query(self, query, variables=None):
        payload = {"query": query, "variables": variables or {}}
        try:
            response = requests.post(self.endpoint, json=payload, headers=self.headers, timeout=15)
            
            # --- أداة تشخيص: لطباعة الاستجابة الحقيقية من السيرفر ---
            print(f"DEBUG: Status Code: {response.status_code}")
            print(f"DEBUG: Response Body: {response.text[:1000]}") # طباعة أول 1000 حرف
            # ----------------------------------------------------
            
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, dict) else {}
        except Exception as e:
            print(f"⚠️ Bridge Engine Error: {e}")
            return {}

    def fetch_latest_products(self, limit=10, page=1):
        query = """
        query GetProducts($limit: Int, $page: Int) {
            findAllProducts(input: { limit: $limit, page: $page }) {
                data {
                    title
                    quantity
                    pricing {
                        price
                    }
                }
            }
        }
        """
        variables = {"limit": limit, "page": page}
        result = self.execute_query(query, variables)
        
        # استخدام .get() بأمان تام في كل خطوة
        data_wrapper = result.get('data')
        if not isinstance(data_wrapper, dict):
            return []
            
        find_all = data_wrapper.get('findAllProducts')
        if not isinstance(find_all, dict):
            return []
            
        products = find_all.get('data')
        
        return products if isinstance(products, list) else []
