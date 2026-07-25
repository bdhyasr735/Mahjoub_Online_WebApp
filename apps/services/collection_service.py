# apps/services/graphql_client.py

import os
import requests
import logging
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class GraphQLClient:
    """عميل GraphQL موحد"""
    
    def __init__(self):
        self.endpoint = os.environ.get('GRAPHQL_ENDPOINT', 'https://mahjoub.online/admin/graphql')
        self.api_key = os.environ.get('QUMRA_API_KEY')
        self.session = self._setup_session()
    
    def _setup_session(self):
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        session.mount("https://", HTTPAdapter(max_retries=retry))
        return session
    
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def execute(self, query: str, variables: Optional[Dict] = None) -> Optional[Dict]:
        """تنفيذ استعلام GraphQL"""
        try:
            response = self.session.post(
                self.endpoint,
                json={'query': query, 'variables': variables or {}},
                headers=self._headers(),
                timeout=30
            )
            
            if response.status_code != 200:
                logging.error(f"HTTP {response.status_code}")
                return None
            
            result = response.json()
            if result.get('errors'):
                logging.error(f"GraphQL Errors: {result['errors']}")
                return None
            
            return result.get('data', {})
            
        except Exception as e:
            logging.error(f"Request failed: {str(e)}")
            return None
