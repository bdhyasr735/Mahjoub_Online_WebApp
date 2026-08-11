import os
import requests
from flask import current_app

class GraphQLClient:
    def __init__(self, endpoint=None, timeout=15):
        # جلب رابط قمرة كلاود الخارجي
        self.endpoint = endpoint or os.environ.get('GRAPHQL_ENDPOINT') or 'https://api.qumra.sa/graphql'
        self.api_key = os.environ.get('QUMRA_API_KEY')
        self.timeout = timeout
        
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'MahjoubOnline-Server/2.0'
        }
        
        if self.api_key:
            self.headers['Authorization'] = f"Bearer {self.api_key}" if not self.api_key.startswith('qmr') else self.api_key

    def execute(self, query, variables=None, operation_name=None):
        # حماية لمنع الاتصال بالذات
        if 'mahjoub.online' in self.endpoint or '127.0.0.1' in self.endpoint:
            raise ValueError("خطأ: لا يمكن توجيه GraphQLClient إلى النطاق المحلي. يجب استخدام رابط قمرة كلاود الخارجي.")

        payload = {
            'query': query,
            'variables': variables or {},
            'operationName': operation_name
        }

        response = requests.post(self.endpoint, json=payload, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
