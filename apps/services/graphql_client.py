import requests
import os
import logging
import urllib3
from requests.adapters import HTTPAdapter

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
        # تم تحديث الاستعلام ليتوافق مع هيكلية Schema المذكورة
        # نفترض أن findAllProducts تعيد كائناً يحتوي على قائمة المنتجات داخل حقل مثل 'items' أو 'nodes'
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
                data = response.json().get('data', {}).get('findAllProducts', {})
                # استخراج البيانات من 'items' بناءً على المخطط
                return data.get('items', [])
            else:
                logging.error(f"خطأ HTTP: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logging.error(f"فشل الاتصال: {str(e)}")
            return []
