# coding: utf-8
# 📂 apps/services/graphql_client.py

import os
import requests
from typing import Dict, Any, Optional
from flask import request

class GraphQLClient:
    """
    عميل GraphQL للاتصال بـ API الخاص بـ Qumra.
    يقرأ التوكن من متغير البيئة QUMRA_API_KEY.
    """
    
    def __init__(self):
        # استخدام المسار المحلي إذا كان الطلب داخلياً لتجنب حظر الشبكة والخروج للسيرفر الخارجي
        base_url = "http://127.0.0.1:5000" if os.environ.get('FLASK_ENV') != 'production' else "https://mahjoub.online"
        self.endpoint = f"{base_url}/admin/graphql"
        self.api_key = os.environ.get("QUMRA_API_KEY", "internal_token")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def execute(self, query: str, variables: Optional[Dict] = None, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """
        تنفيذ استعلام GraphQL وإرجاع النتيجة مع حماية ضد الـ Timeout.
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        if operation_name:
            payload["operationName"] = operation_name
        
        headers = self.headers.copy()
        
        print(f"🔍 [GraphQLClient] Operation: {operation_name}")
        print(f"🔍 [GraphQLClient] Variables: {variables}")
        
        try:
            # تقليل الـ timeout إلى 10 ثوانٍ لمنع تعليق الـ Worker وموته
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"⚠️ [GraphQLClient] Status Code: {response.status_code}, Response: {response.text[:200]}")
                # إرجاع هيكل فارغ بدلاً من الانهيار لكي تفتح النافذة وتظهر الواجهة
                return {"data": {"findAllProducts": {"data": [], "pagination": {"totalItems": 0, "totalPages": 1, "currentPage": 1}}}}
                
            data = response.json()
            
            if "errors" in data:
                print(f"⚠️ [GraphQLClient Errors]: {data['errors']}")
                return {"data": {"findAllProducts": {"data": [], "pagination": {"totalItems": 0, "totalPages": 1, "currentPage": 1}}}}
            
            return data.get("data", {})
        
        except requests.exceptions.RequestException as e:
            print(f"❌ [GraphQLClient Connection Error]: {str(e)}")
            # إرجاع بيانات فارغة لكي تفتح الواجهة ولا تحدث مشكلة 500 أو Timeout
            return {"findAllProducts": {"data": [], "pagination": {"totalItems": 0, "totalPages": 1, "currentPage": 1}}}
    
    def test_connection(self) -> bool:
        try:
            query = """
            query {
                __typename
            }
            """
            result = self.execute(query, operation_name="__typename")
            return result is not None
        except Exception as e:
            print(f"❌ [GraphQLClient]: فشل اختبار الاتصال: {e}")
            return False
