import requests
import os
import logging
import urllib3
from requests.adapters import HTTPAdapter

# إيقاف تحذيرات SSL لضمان استقرار الاتصال بـ API قمرة
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class QomrahGraphQLClient:
    BASE_URL = "https://api.qomrah.com/graphql"
    
    @staticmethod
    def _get_headers(extra_headers=None):
        api_key = os.environ.get('QUMRA_API_KEY')
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Connection": "keep-alive"
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers

    @staticmethod
    def fetch_products(headers=None):
        # الاستعلام المتوافق مع الـ Schema المكتشفة: findAllProducts
        query = """
        query { 
          findAllProducts(page: 1, limit: 100) { 
            items { 
              _id 
              title 
              price 
              sku 
            }
          } 
        }
        """
        
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=3))
        
        try:
            final_headers = QomrahGraphQLClient._get_headers(extra_headers=headers)
            
            response = session.post(
                QomrahGraphQLClient.BASE_URL,
                json={'query': query},
                headers=final_headers,
                verify=False,
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                # التحقق من وجود أخطاء في استجابة GraphQL نفسها (GraphQL Errors)
                if 'errors' in result:
                    logging.error(f"أخطاء في استعلام GraphQL: {result['errors']}")
                    return []
                
                data = result.get('data', {}).get('findAllProducts', {})
                return data.get('items', [])
            
            else:
                # تسجيل تفاصيل الخطأ لتشخيص الـ 502
                logging.error(f"فشل الاتصال - كود الحالة: {response.status_code}")
                logging.error(f"محتوى الخطأ: {response.text[:500]}")
                return []
                
        except Exception as e:
            logging.error(f"استثناء أثناء المزامنة: {str(e)}")
            return []
