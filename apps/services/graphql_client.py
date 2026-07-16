import requests
import os
import logging
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# إيقاف تحذيرات SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class QomrahGraphQLClient:
    BASE_URL = "https://api.qomrah.com/graphql"
    
    @staticmethod
    def _get_session():
        """إنشاء جلسة مع استراتيجية إعادة محاولة ذكية للأخطاء المؤقتة"""
        session = requests.Session()
        # محاولة إعادة الاتصال عند حدوث أخطاء خادم (5xx)
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        return session

    @staticmethod
    def execute_query(query, variables=None):
        """دالة عامة لتنفيذ أي استعلام GraphQL"""
        api_key = os.environ.get('QUMRA_API_KEY')
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        session = QomrahGraphQLClient._get_session()
        try:
            response = session.post(
                QomrahGraphQLClient.BASE_URL,
                json={'query': query, 'variables': variables},
                headers=headers,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            if 'errors' in result:
                logging.error(f"GraphQL Errors: {result['errors']}")
                return None
            return result.get('data')
            
        except Exception as e:
            logging.error(f"خطأ أثناء الاتصال بـ GraphQL: {str(e)}")
            return None
