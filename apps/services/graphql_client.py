# coding: utf-8
# 📂 apps/services/graphql_client.py

import requests
import os
import logging
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# تعطيل تحذيرات الـ SSL لتجنب إزعاج الـ Logs عند استخدام verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# إنشاء جلسة واحدة ثابتة تُستخدم طوال عمر التطبيق لتسريع الاتصالات
_session = requests.Session()
_retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
_adapter = HTTPAdapter(max_retries=_retry_strategy)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter) # تمت إضافتها تحسباً لأي تحويل داخلي

class QomrahGraphQLClient:
    """
    كلاس مُحسن لإدارة طلبات GraphQL بكفاءة عالية
    """
    
    BASE_URL = "https://mahjoub.online/admin/graphql"
    
    @staticmethod
    def execute_query(query, variables=None):
        """تنفيذ استعلام GraphQL باستخدام الجلسة الثابتة"""
        api_key = os.environ.get('QUMRA_API_KEY')
        
        if not api_key:
            logging.error("❌ مفتاح API (QUMRA_API_KEY) مفقود")
            return None

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Qomrah-Sync-Engine/1.0)"
        }
        
        try:
            # استخدام الجلسة الثابتة _session وتقليل الـ timeout لـ 10 ثواني
            response = _session.post(
                QomrahGraphQLClient.BASE_URL,
                json={'query': query, 'variables': variables},
                headers=headers,
                verify=False,
                timeout=10 
            )
            
            if response.status_code != 200:
                logging.error(f"❌ GraphQL Status {response.status_code}: {response.text}")
                return None
            
            result = response.json()
            
            if 'errors' in result:
                logging.error(f"❌ GraphQL Logic Error: {result['errors']}")
                return None
            
            return result.get('data')
            
        except requests.exceptions.RequestException as req_err:
            logging.error(f"❌ خطأ في الشبكة أو الاتصال: {str(req_err)}")
            return None
        except Exception as e:
            logging.error(f"❌ خطأ غير متوقع: {str(e)}")
            return None
