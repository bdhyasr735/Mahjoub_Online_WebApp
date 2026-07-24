# coding: utf-8
# 📂 apps/services/graphql_client.py

import requests
import os
import logging
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ✅ للتحقق من وجود المفتاح عند بدء التشغيل
print(f"🔍 QUMRA_API_KEY exists: {bool(os.environ.get('QUMRA_API_KEY'))}")
print(f"🔍 GRAPHQL_ENDPOINT: {os.environ.get('GRAPHQL_ENDPOINT', 'NOT SET')}")

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

    @staticmethod
    def get_base_url():
        # ✅ التعديل هنا ليدعم GRAPHQL_ENDPOINT الموجود في Render
        return (
            os.environ.get('GRAPHQL_ENDPOINT') or 
            os.environ.get('QUMRA_API_URL') or 
            'https://mahjoub.online/admin/graphql'
        )

    @staticmethod
    def execute_query(query, variables=None):
        # ✅ إضافة تصحيح للتحقق من الاتصال
        print(f"🔍 Executing GraphQL query to: {QomrahGraphQLClient.get_base_url()}")
        
        api_key = (
            os.environ.get('QUMRA_API_KEY') or 
            os.environ.get('ADMIN_JWT_TOKEN')
        )
        target_url = QomrahGraphQLClient.get_base_url()

        if not api_key:
            logging.error("❌ مفتاح API (QUMRA_API_KEY) مفقود في متغيرات البيئة.")
            print("❌ QUMRA_API_KEY is missing!")
            return None

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Qomrah-Sync-Engine/1.0)"
        }

        try:
            print(f"🔄 Sending request with query length: {len(query)} characters")
            response = _session.post(
                target_url,
                json={'query': query, 'variables': variables},
                headers=headers,
                verify=False,
                timeout=30  # ✅ زيادة المهلة إلى 30 ثانية
            )

            print(f"📡 Response Status: {response.status_code}")
            
            if response.status_code != 200:
                logging.error(f"❌ GraphQL Status {response.status_code}: {response.text[:500]}")
                print(f"❌ HTTP Error {response.status_code}: {response.text[:500]}")
                return None

            result = response.json()

            if 'errors' in result:
                logging.error(f"❌ GraphQL Logic Error: {result['errors']}")
                print(f"❌ GraphQL Logic Error: {result['errors']}")
                return None

            print("✅ GraphQL query executed successfully")
            return result

        except requests.exceptions.Timeout:
            logging.error("❌ طلب GraphQL انتهى وقته (Timeout)")
            print("❌ GraphQL Request Timeout")
            return None
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"❌ خطأ في الاتصال: {str(conn_err)}")
            print(f"❌ Connection Error: {str(conn_err)}")
            return None
        except requests.exceptions.RequestException as req_err:
            logging.error(f"❌ خطأ في الشبكة أثناء الاتصال: {str(req_err)}")
            print(f"❌ Request Exception: {str(req_err)}")
            return None
        except Exception as e:
            logging.error(f"❌ خطأ غير متوقع: {str(e)}")
            print(f"❌ Unexpected Error: {str(e)}")
            return None
