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
        """إعداد الجلسة مع استراتيجية إعادة المحاولة عند حدوث أخطاء"""
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
        """تنفيذ استعلام GraphQL وإرجاع البيانات الخام"""
        api_key = os.environ.get('QUMRA_API_KEY')
        
        # التحقق من وجود مفتاح الـ API
        if not api_key:
            logging.error("❌ مفتاح API (QUMRA_API_KEY) مفقود")
            return None

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Qomrah-Sync-Engine/1.0)"
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
            
            # تسجيل أخطاء البروتوكول (400, 401, 500)
            if response.status_code != 200:
                logging.error(f"❌ GraphQL Status {response.status_code}: {response.text}")
                return None
            
            result = response.json()
            
            # تسجيل أخطاء الـ GraphQL (التي تأتي داخل الـ JSON)
            if 'errors' in result:
                logging.error(f"❌ GraphQL Logic Error: {result['errors']}")
                return None
            
            # إرجاع الـ data ليتمكن الـ route من استخراج النتائج بسهولة
            return result.get('data')
            
        except Exception as e:
            # معالجة الأخطاء غير المتوقعة في الاتصال
            logging.error(f"❌ خطأ غير متوقع في الاتصال: {str(e)}")
            return None
