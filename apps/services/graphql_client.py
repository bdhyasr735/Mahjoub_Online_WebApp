# coding: utf-8
# 📂 apps/services/graphql_client.py

import requests
import os
import logging
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# تعطيل تحذيرات الـ SSL عند استخدام verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# تهيئة الجلسة (Session) مع استراتيجية إعادة المحاولة (Retry Strategy)
_session = requests.Session()
_retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST"]
)
_adapter = HTTPAdapter(max_retries=_retry_strategy)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)

class QomrahGraphQLClient:
    """
    كلاس مُحسن لإدارة طلبات GraphQL بكفاءة عالية للتواصل مع منصة Mahjoub Online
    """
    
    @staticmethod
    def get_base_url():
        """جلب رابط API ديناميكياً من متغيرات البيئة مع خيار افتراضي آمن"""
        return os.environ.get('QOMRA_GRAPHQL_URL', 'https://mahjoub.online/admin/graphql')

    @staticmethod
    def execute_query(query, variables=None):
        """تنفيذ استعلام أو Mutation لـ GraphQL باستخدام الجلسة الثابتة"""
        api_key = os.environ.get('QUMRA_API_KEY')
        target_url = QomrahGraphQLClient.get_base_url()
        
        if not api_key:
            logging.error("❌ مفتاح API (QUMRA_API_KEY) مفقود في متغيرات البيئة.")
            return None

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Qomrah-Sync-Engine/1.0)"
        }
        
        try:
            # تنفيذ الطلب باستخدام الجلسة والرابط الديناميكي
            response = _session.post(
                target_url,
                json={'query': query, 'variables': variables},
                headers=headers,
                verify=False,
                timeout=15 
            )
            
            # التحقق من حالة استجابة HTTP
            if response.status_code != 200:
                logging.error(f"❌ GraphQL Status {response.status_code}: {response.text}")
                return None
            
            result = response.json()
            
            # التحقق من وجود أخطاء منطقية داخل استجابة GraphQL
            if 'errors' in result:
                logging.error(f"❌ GraphQL Logic Error: {result['errors']}")
                return None
            
            return result
            
        except requests.exceptions.RequestException as req_err:
            logging.error(f"❌ خطأ في الشبكة أثناء الاتصال بـ قمرة: {str(req_err)}")
            return None
        except Exception as e:
            logging.error(f"❌ خطأ غير متوقع في خدمة GraphQL: {str(e)}")
            return None
