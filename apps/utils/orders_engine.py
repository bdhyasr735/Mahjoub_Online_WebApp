# coding: utf-8
# 📂 apps/utils/bridge_engine.py

import requests
import os
import logging

logger = logging.getLogger(__name__)

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
            return response.json()
        except Exception as e:
            logger.error(f"⚠️ Connection Error: {e}")
            return {}

    # تأكد من وجود هذه الدالة هنا بالضبط:
    def fetch_latest_orders(self):
        query = """
        query {
            findAllOrders(input: { limit: 20, page: 1 }) {
                data {
                    _id
                    totalPrice
                    status { name }
                    account { name }
                }
            }
        }
        """
        result = self.execute_query(query)
        if 'errors' in result:
            logger.error(f"⚠️ GraphQL Errors: {result['errors']}")
            return []
        return result.get('data', {}).get('findAllOrders', {}).get('data', [])

    def fetch_latest_products(self):
        # ... (بقية كود المنتجات الخاص بك كما هو) ...
        pass
