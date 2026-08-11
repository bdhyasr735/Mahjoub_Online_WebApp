# coding: utf-8
# 📂 apps/services/graphql_client.py

import os
import logging
import requests

logger = logging.getLogger(__name__)


class GraphQLClient:
    """عميل برميجي لإدارة وإرسال الاستعلامات عبر GraphQL لمنصة قُمرة (Qumra)"""

    def __init__(self, endpoint=None, api_key=None, timeout=30):
        # الاعتماد على العنوان الافتراضي لقمرا إن لم يتم التمرير
        self.endpoint = endpoint or os.getenv("GRAPHQL_ENDPOINT", "https://api.qumra.cloud/graphql")
        self.api_key = api_key or os.getenv("QUMRA_API_KEY", "")
        self.timeout = timeout
        self.session = requests.Session()

    def _get_headers(self):
        """تجهيز وتنظيف الترويسات لضمان التوثيق المعتمد لدى قمرا"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if self.api_key:
            clean_key = self.api_key.strip()

            # إزالة كلمة Bearer إذا كانت معرّفة مسبقاً داخل المتغير
            if clean_key.lower().startswith("bearer "):
                clean_key = clean_key[7:].strip()

            # إرسال التوثيق بالصيغتين (Standard Bearer & x-api-key) لضمان توافق سيرفر قمرا
            headers["Authorization"] = f"Bearer {clean_key}"
            headers["x-api-key"] = clean_key

        return headers

    def execute(self, query, variables=None, operation_name=None):
        """تنفيذ استعلام GraphQL وإرجاع النتيجة بصيغة Dict"""
        if not query:
            return {"errors": [{"message": "Query string cannot be empty."}]}

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
                timeout=self.timeout
            )

            try:
                res_data = response.json()

                if response.status_code != 200 or "errors" in res_data:
                    logger.error(f"❌ [Qumra Response Error] HTTP {response.status_code}: {res_data}")

                return res_data

            except ValueError:
                logger.error(f"❌ [GraphQL Non-JSON Response] HTTP {response.status_code}: {response.text}")
                return {
                    "errors": [
                        {"message": f"Server returned non-JSON response with status {response.status_code}"}
                    ]
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ [GraphQL Network Error]: {str(e)}")
            return {"errors": [{"message": f"Network error occurred: {str(e)}"}]}
