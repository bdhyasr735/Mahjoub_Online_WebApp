# coding: utf-8
# 🌐 عميل الاتصال بـ GraphQL - منصة محجوب أونلاين 2026

import requests
from typing import Optional, Dict, Any
from config import Config


class GraphQLClient:
    """عميل الاتصال بـ GraphQL API لمتجر محجوب أونلاين"""
    
    def __init__(self, endpoint: Optional[str] = None, api_key: Optional[str] = None):
        self.endpoint = endpoint or Config.QUMRA_API_URL
        self.api_key = api_key or Config.QUMRA_API_KEY
        
        if not self.api_key:
            print("⚠️ [GraphQLClient]: تحذير: مفتاح المصادقة QUMRA_API_KEY غير موجود!")
    
    def get_headers(self) -> Dict[str, str]:
        """إعداد الترويسات (Headers) المطلوبة للاتصال مع توثيق الـ Bearer"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.api_key:
            token = self.api_key.strip()
            # التعامل الذكي في حال كان المفتاح مسبوقاً بكلمة Bearer أو لا
            if not token.lower().startswith("bearer "):
                headers["Authorization"] = f"Bearer {token}"
            else:
                headers["Authorization"] = token
                
        return headers
    
    def execute(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        تنفيذ استعلام أو عملية تعديل (Query / Mutation) عبر GraphQL
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
            
        headers = self.get_headers()
        
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    print(f"❌ [GraphQL Errors]: {result['errors']}")
                return result.get("data")
            else:
                print(f"❌ [HTTP Error {response.status_code}]: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ [Connection Exception]: {e}")
            return None
