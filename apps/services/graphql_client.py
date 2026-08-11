# coding: utf-8
# 📂 apps/services/graphql_client.py

import os
import requests
from flask import current_app

class GraphQLClient:
    def __init__(self, endpoint=None, timeout=15):
        # القراءة من إعدادات Qumra أو المتغير البيئي
        if endpoint:
            self.endpoint = endpoint
        elif current_app and current_app.config.get('QUMRA_API_URL'):
            self.endpoint = current_app.config.get('QUMRA_API_URL')
        else:
            self.endpoint = os.environ.get('GRAPHQL_ENDPOINT')

        self.api_key = os.environ.get('QUMRA_API_KEY') or (current_app.config.get('QUMRA_API_KEY') if current_app else None)
        self.timeout = timeout
        
        # إعداد الترويسات المطلوبة للاتصال بقمرة
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'MahjoubOnline-Server/2.0'
        }
        
        if self.api_key:
            self.headers['Authorization'] = f"Bearer {self.api_key}"

    def execute(self, query, variables=None, operation_name=None):
        if not self.endpoint or 'mahjoub.online' in self.endpoint or '127.0.0.1' in self.endpoint:
            raise Exception("خطأ في الإعدادات: رابط Qumra GraphQL يشاركه السيرفر مع نفسه بمسار مجوف. يرجى توجيه GRAPHQL_ENDPOINT لرابط قمرة كلاود الفعلي.")

        payload = {
            'query': query,
            'variables': variables or {},
            'operationName': operation_name
        }
        
        print(f"🔍 [GraphQLClient] جاري إرسال الطلب لـ Qumra Cloud: {self.endpoint}")

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
            print(f"❌ [GraphQLClient Error]: انتهت مهلة الاتصال بخادم قمرة ({self.timeout} ثوانٍ)")
            raise Exception("انتهت مهلة الاتصال بخادم قمرة كلاود.")
        except requests.exceptions.RequestException as e:
            print(f"❌ [GraphQLClient Connection Error]: {str(e)}")
            raise Exception(f"فشل الاتصال بقمرة كلاود: {str(e)}")
