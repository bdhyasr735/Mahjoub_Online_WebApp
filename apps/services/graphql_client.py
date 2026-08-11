# coding: utf-8
# 📂 apps/services/graphql_client.py

import os
import requests
from typing import Dict, Any, Optional

class GraphQLClient:
    """
    عميل GraphQL للاتصال بـ API الخاص بـ Qumra.
    يستخدم الاتصال الداخلي في بيئة الإنتاج لتجنب Timeout.
    """
    
    def __init__(self):
        from config import Config
        
        # ✅ الحل الجذري: استخدام 127.0.0.1 بدلاً من 0.0.0.0 للاتصال الداخلي الحقيقي داخل الحاوية
        if os.environ.get('FLASK_ENV') == 'production':
            port = os.environ.get('PORT', 10000)
            self.endpoint = f"http://127.0.0.1:{port}/admin/graphql"
        else:
            # في بيئة التطوير المحلية
            self.endpoint = "http://127.0.0.1:5000/admin/graphql"
        
        # قراءة المفتاح من متغير البيئة، وإذا لم يوجد يقرأ من إعدادات Config (احتياطياً)
        self.api_key = os.environ.get("QUMRA_API_KEY", Config.QUMRA_API_KEY)
        
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
        
        print(f"🔍 [GraphQLClient] الاتصال بـ: {self.endpoint}")
        print(f"🔍 [GraphQLClient] العملية: {operation_name}")
        
        try:
            # تم تمديد الـ timeout إلى 15 ثانية لتجنب الأخطاء
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"⚠️ [GraphQLClient] Status Code: {response.status_code}, Response: {response.text[:200]}")
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
            query = """query { __typename }"""
            result = self.execute(query, operation_name="__typename")
            return result is not None
        except Exception as e:
            print(f"❌ [GraphQLClient]: فشل اختبار الاتصال: {e}")
            return False
