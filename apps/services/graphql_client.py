# coding: utf-8
import requests
from typing import Optional, Dict, Any
from config import Config

class GraphQLClient:
    def __init__(self, endpoint: Optional[str] = None, api_key: Optional[str] = None):
        self.endpoint = endpoint or Config.QUMRA_API_URL
        self.api_key = api_key or Config.QUMRA_API_KEY
        
    def get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.api_key:
            token = self.api_key.strip()
            if not token.lower().startswith("bearer "):
                headers["Authorization"] = f"Bearer {token}"
            else:
                headers["Authorization"] = token
        return headers
    
    def execute(self, query: str, variables: Optional[Dict[str, Any]] = None, operation_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """تنفيذ استعلام مع دعم تحديد اسم العملية (operationName) لملفات الـ GraphQL المتعددة"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        if operation_name:
            payload["operationName"] = operation_name
            
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
