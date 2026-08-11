# coding: utf-8
# 📂 apps/services/graphql_client.py

import os
import logging
import requests
import json

logger = logging.getLogger(__name__)

class GraphQLClient:
    def __init__(self, endpoint=None, api_key=None, timeout=25):
        # تجنب استخدام mahjoub.online لمنع الـ Self-Loopback
        default_endpoint = 'https://api.qumra.cloud/graphql'
        
        env_endpoint = os.environ.get('GRAPHQL_ENDPOINT') or os.environ.get('QUMRA_GRAPHQL_ENDPOINT')
        
        if env_endpoint and 'mahjoub.online' in env_endpoint:
            env_endpoint = None

        self.endpoint = endpoint or env_endpoint or default_endpoint
        
        self.api_key = (
            api_key or
            os.environ.get('QUMRA_API_KEY') or
            os.environ.get('GRAPHQL_API_KEY') or
            ''
        )
        
        self.timeout = timeout
        self.session = requests.Session()

    def _get_headers(self):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'MahjoubOnline-GraphQLClient/2.0'
        }
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"
            headers['X-Api-Key'] = self.api_key
            headers['Qumra-Api-Key'] = self.api_key
        return headers

    def execute(self, query, variables=None, operation_name=None):
        if not query:
            return {"errors": [{"message": "Query is empty."}]}

        payload = {
            "query": query,
            "variables": variables or {},
            "operationName": operation_name
        }

        try:
            response = self.session.post(
                self.endpoint,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout,
                verify=True
            )
            
            # طباعة تشخيصية في حالة أرجع الخادم كود غير 200
            if response.status_code != 200:
                logger.error(f"⚠️ [GraphQLClient] الخادم أرجع الحالة {response.status_code} من {self.endpoint}")

            # المحاولة الأولى: تحويل الاستجابة إلى JSON
            try:
                return response.json()
            except (json.JSONDecodeError, ValueError) as json_err:
                # إذا كانت الاستجابة ليست JSON (مثلاً HTML)، قم بطباعة أجزاء منها للتشخيص
                preview = response.text[:300].replace('\n', ' ')
                logger.error(f"❌ [GraphQLClient Error]: الاستجابة ليست JSON. الكود: {response.status_code} | المحتوى: {preview}")
                return {
                    "errors": [{
                        "message": f"الاستجابة المرتجعة من ({self.endpoint}) ليست بصيغة JSON (HTTP {response.status_code})."
                    }]
                }

        except requests.exceptions.Timeout:
            logger.error(f"❌ [GraphQLClient]: انتهت مهلة الاتصال بالخادم ({self.endpoint})")
            return {"errors": [{"message": f"انتهت مهلة الاتصال بالخادم الخارجي ({self.timeout} ثوانٍ)."}]}
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ [GraphQLClient Request Error]: {str(e)}")
            return {"errors": [{"message": f"فشل الاتصال بـ API الخارجي: {str(e)}"}]}

    def test_connection(self):
        try:
            result = self.execute("{ __typename }")
            return isinstance(result, dict) and ("data" in result or "errors" in result)
        except Exception:
            return False
