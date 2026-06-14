# 📂 apps/utils/bridge_engine.py
import requests
from config import Config
import logging

logger = logging.getLogger(__name__)

class QumraBridgeEngine:
    def __init__(self):
        self.endpoint = Config.QUMRA_API_URL
        self.headers = {
            "Authorization": f"Bearer {Config.QUMRA_API_KEY}",
            "Content-Type": "application/json"
        }

    def fetch_products_from_qumra(self, search_term="", page=1):
        """
        استعلام استكشافي (Introspection Query) لمعرفة الهيكل الصحيح للـ API.
        """
        # هذا الاستعلام سيجلب لنا أسماء الحقول المتاحة في ProductsResponse
        query = """
        query {
            __type(name: "ProductsResponse") {
                fields {
                    name
                    type {
                        name
                        kind
                    }
                }
            }
        }
        """
        
        try:
            response = requests.post(
                self.endpoint, 
                json={"query": query}, 
                headers=self.headers, 
                timeout=15
            )
            
            # --- تسجيل الهيكل الحقيقي في الـ Logs ---
            # هذا السجل هو مفتاح الحل، ستعرف منه الاسم الصحيح للحقل المطلوب
            logger.info(f"DEBUG_SCHEMA_RESPONSE: {response.text}")
            
            # نرجع قائمة فارغة حالياً لأننا في مرحلة الاستكشاف
            return []
                
        except Exception as e:
            logger.error(f"Exception during exploration: {str(e)}")
            return []

    def sync_all_data(self):
        return True
