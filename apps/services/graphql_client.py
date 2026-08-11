# coding: utf-8
# 📂 apps/services/graphql_client.py

import os
import requests
from flask import current_app

class GraphQLClient:
    def __init__(self, endpoint=None, timeout=15):
        # 1. القراءة أولاً من المتغير التقديمي أو Config أو البيئة مباشر
        if endpoint:
            self.endpoint = endpoint
        elif current_app and current_app.config.get('QUMRA_API_URL'):
            self.endpoint = current_app.config.get('QUMRA_API_URL')
        else:
            self.endpoint = os.environ.get('GRAPHQL_ENDPOINT', 'https://mahjoub.online/admin/graphql')
        
        self.timeout = timeout
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'MahjoubOnline-Server/2.0'
        }

    def execute(self, query, variables=None, operation_name=None):
        payload = {
            'query': query,
            'variables': variables or {},
            'operationName': operation_name
        }
        
        print(f"🔍 [GraphQLClient] الاتصال بـ: {self.endpoint}")
        print(f"🔍 [GraphQLClient] العملية: {operation_name}")

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            print(f"❌ [GraphQLClient Error]: انتهت مهلة الاتصال بالخادم ({self.timeout} ثوانٍ)")
            raise Exception("انتهت مهلة الاتصال بالخادم الرئيسي أثناء المزامنة.")
        except requests.exceptions.RequestException as e:
            print(f"❌ [GraphQLClient Connection Error]: {str(e)}")
            raise Exception(f"فشل الاتصال بمركز البيانات: {str(e)}")

    def test_connection(self):
        test_query = "{ __typename }"
        try:
            res = self.execute(test_query)
            return "data" in res
        except Exception:
            return False
