# coding: utf-8
# 📂 apps/services/graphql_client.py

import requests
import os
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Any, Optional

# إعدادات الجلسة مع آلية إعادة المحاولة تلقائياً
_session = requests.Session()
_retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST"]
)
_session.mount("https://", HTTPAdapter(max_retries=_retry_strategy))
_session.mount("http://", HTTPAdapter(max_retries=_retry_strategy))


class GraphQLClient:
    """عميل GraphQL متطور - يدعم التنفيذ وإدارة التوثيق"""
    
    def __init__(self, endpoint: str = None, api_key: str = None):
        self.endpoint = endpoint or os.environ.get('GRAPHQL_ENDPOINT', 'https://mahjoub.online/admin/graphql')
        self.api_key = api_key or os.environ.get('QUMRA_API_KEY')
        
    def _get_headers(self) -> Dict:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def execute(self, query: str, variables: Optional[Dict] = None) -> Optional[Dict]:
        """تنفيذ أي استعلام أو تعديل GraphQL"""
        try:
            response = _session.post(
                self.endpoint,
                json={'query': query, 'variables': variables or {}},
                headers=self._get_headers(),
                timeout=30
            )
            
            if response.status_code != 200:
                logging.error(f"HTTP {response.status_code}: {response.text[:200]}")
                return None
                
            result = response.json()
            if 'errors' in result:
                logging.error(f"GraphQL Errors: {result['errors']}")
                return None
                
            return result.get('data', {})
            
        except Exception as e:
            logging.error(f"Request failed: {str(e)}")
            return None
