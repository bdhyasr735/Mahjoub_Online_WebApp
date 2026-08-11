# coding: utf-8
import os
import requests

class GraphQLClient:
    """عميل GraphQL للاتصال بمتجر قمرة (mahjoub.online)"""
    
    def __init__(self, endpoint=None, timeout=15):
        # الرابط المباشر لمنصة قمرة (https://mahjoub.online/admin/graphql)
        self.endpoint = endpoint or os.environ.get('GRAPHQL_ENDPOINT') or 'https://mahjoub.online/admin/graphql'
        self.api_key = os.environ.get('QUMRA_API_KEY') or os.environ.get('QUMRA_API_ENDPOINT')
        self.timeout = timeout
        
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'MahjoubOnline-Server/2.0'
        }
        
        if self.api_key:
            self.headers['Authorization'] = self.api_key if self.api_key.startswith('qmr') else f"Bearer {self.api_key}"

    def execute(self, query, variables=None, operation_name=None):
        payload = {
            'query': query,
            'variables': variables or {},
        }
        if operation_name:
            payload['operationName'] = operation_name

        try:
            response = requests.post(self.endpoint, json=payload, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            res_data = response.json()
            
            # في حال وجود أخطاء من قمرة يتم طباعتها للتشخيص
            if "errors" in res_data and res_data["errors"]:
                print(f"⚠️ [GraphQLClient] أخطاء من قمرة: {res_data['errors']}")
                
            return res_data.get('data', {})
        except Exception as e:
            print(f"❌ [GraphQLClient] خطأ في الاتصال بـ ({self.endpoint}): {e}")
            raise e
