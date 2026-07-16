# coding: utf-8
# 📂 apps/services/graphql_client.py

import requests
import os
import logging
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# تعطيل تحذيرات الـ SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class QomrahGraphQLClient:
    """
    كلاس موحد لإدارة طلبات GraphQL إلى API الخاص بـ 'محجوب'
    """
    
    BASE_URL = "https://mahjoub.online/admin/graphql"
    
    @staticmethod
    def _get_session():
        session = requests.Session()
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
        """تنفيذ استعلام GraphQL وإرجاع البيانات مع تسجيل تفصيلي للأخطاء."""
        api_key = os.environ.get('QUMRA_API_KEY')
        
        if not api_key:
            logging.error("❌ مفتاح API (QUMRA_API_KEY) غير موجود في إعدادات البيئة")
            return None

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Compatible; Qomrah-Sync-Engine/1.0)"
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
            
            # تسجيل الحالة إذا كان هناك خطأ (مثل 400 Bad Request)
            if response.status_code != 200:
                logging.error(f"❌ GraphQL Server returned status {response.status_code}")
                logging.error(f"❌ Response details: {response.text}") # هذا السطر هو مفتاح الحل
                return None
            
            result = response.json()
            
            # معالجة أخطاء GraphQL البرمجية
            if 'errors' in result:
                logging.error(f"❌ GraphQL API Logic Errors: {result['errors']}")
                return None
                
            return result.get('data')
            
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ خطأ في الاتصال الشبكي بـ {QomrahGraphQLClient.BASE_URL}: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"❌ خطأ غير متوقع في معالجة البيانات: {str(e)}")
            return None
