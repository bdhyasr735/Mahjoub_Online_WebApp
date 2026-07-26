# coding: utf-8
# 📂 apps/services/graphql_client.py

import os
import requests
from typing import Dict, Any, Optional

class GraphQLClient:
    """
    عميل GraphQL للاتصال بـ API الخاص بـ Qumra.
    يقرأ التوكن من متغير البيئة QUMRA_API_KEY.
    """
    
    def __init__(self):
        self.endpoint = "https://mahjoub.online/admin/graphql"
        self.api_key = os.environ.get("QUMRA_API_KEY")
        
        if not self.api_key:
            raise ValueError("QUMRA_API_KEY غير موجود في متغيرات البيئة!")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def execute(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """
        تنفيذ استعلام GraphQL وإرجاع النتيجة.
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            # التحقق من وجود أخطاء في GraphQL
            if "errors" in data:
                error_messages = [err.get("message", "خطأ غير معروف") for err in data["errors"]]
                raise Exception(f"أخطاء GraphQL: {', '.join(error_messages)}")
            
            return data.get("data", {})
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"فشل الاتصال بـ GraphQL: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        اختبار الاتصال بـ GraphQL API.
        
        Returns:
            bool: True إذا كان الاتصال ناجحاً، False إذا فشل.
        """
        try:
            # استعلام بسيط لاختبار الاتصال
            query = """
            query {
                __typename
            }
            """
            result = self.execute(query)
            return result is not None
        except Exception as e:
            print(f"❌ [GraphQLClient]: فشل اختبار الاتصال: {e}")
            return False
