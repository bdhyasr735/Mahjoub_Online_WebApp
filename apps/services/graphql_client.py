# coding: utf-8
# 📂 apps/services/graphql_client.py

import os
import logging
import requests
from flask import current_app

logger = logging.getLogger(__name__)

class GraphQLClient:
    """
    عميل تنفيذ واستعلامات GraphQL للاتصال بالخدمات الخارجيّة وواجهات API (مثل منصة قمرا Qumra).
    مُصمم لمنع مشكلات إعادة التوجيه (302 Redirect) والحلقات المحلية (Loopback)، مع إدارة معالجة الأخطاء والمهل الزمنية.
    """

    def __init__(self, endpoint=None, api_key=None, timeout=20):
        # جلب الرابط الخارجي المباشر لتجنب الاتصال الذاتي بالخادم المحلي
        self.endpoint = (
            endpoint or
            os.environ.get('GRAPHQL_ENDPOINT') or
            os.environ.get('QUMRA_GRAPHQL_ENDPOINT') or
            (getattr(current_app.config, 'GRAPHQL_ENDPOINT', None) if current_app else None) or
            'https://qumra.online/graphql'
        )
        
        self.api_key = (
            api_key or
            os.environ.get('QUMRA_API_KEY') or
            os.environ.get('GRAPHQL_API_KEY') or
            (getattr(current_app.config, 'QUMRA_API_KEY', None) if current_app else None) or
            ''
        )
        
        self.timeout = timeout
        self.session = requests.Session()

    def _get_headers(self):
        """
        تجهيز الهيدرز المطلوبة وتمرير مفاتيح المصادقة.
        """
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
        """
        تنفيذ استعلام GraphQL أو طفرة (Mutation) وإعادة النتيجة بتنسيق JSON.
        """
        if not query:
            return {"errors": [{"message": "لم يتم تقديم استعلام GraphQL صالح (Query is empty)."}]}

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

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logger.error(f"❌ [GraphQLClient]: انتهت مهلة الاتصال بالخادم ({self.endpoint})")
            return {
                "errors": [{
                    "message": f"انتهت مهلة الاتصال بخادم GraphQL الخارجي ({self.timeout} ثوانٍ)."
                }]
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ [GraphQLClient Error]: {str(e)}")
            return {
                "errors": [{
                    "message": f"فشل الاتصال بـ GraphQL API: {str(e)}"
                }]
            }
        except Exception as e:
            logger.error(f"❌ [GraphQLClient Unexpected Error]: {str(e)}")
            return {
                "errors": [{
                    "message": f"حدث خطأ غير متوقع أثناء معالجة الطلب: {str(e)}"
                }]
            }

    def test_connection(self):
        """
        اختبار استقرار الاتصال بـ GraphQL API وإعادة حالة الجاهزية (True/False).
        """
        test_query = "{ __typename }"
        try:
            result = self.execute(test_query)
            if isinstance(result, dict) and ("data" in result or "errors" in result):
                return True
            return False
        except Exception as e:
            logger.error(f"❌ [GraphQLClient Test Connection Failed]: {str(e)}")
            return False
