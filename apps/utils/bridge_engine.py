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
        استعلام مبسط جداً يتجنب أي وسائط قد تسبب خطأ 400.
        """
        # قمت بإزالة 'data' من داخل الاستعلام تحسباً لأن يكون الـ API 
        # يعيد الحقول مباشرة تحت findAllProducts
        query = """
        query {
            findAllProducts {
                title
                pricing { price }
                quantity
                status
                images { fileUrl }
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
            
            # --- تسجيل الاستجابة الخام في الـ Logs لتشخيص أي خطأ مستقبلي ---
            logger.info(f"DEBUG_RESPONSE: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                # محاولة استخراج البيانات سواء كانت داخل 'data' أو مباشرة
                raw_data = result.get('data', {}).get('findAllProducts', [])
                if not raw_data: # إذا كان الهيكل مختلفاً
                    raw_data = result.get('findAllProducts', [])
                
                all_products = []
                for p in raw_data:
                    images = p.get('images', [])
                    image_url = images[0].get('fileUrl') if images else 'https://via.placeholder.com/150'
                    
                    all_products.append({
                        "title": p.get('title', 'بدون اسم'),
                        "price": p.get('pricing', {}).get('price', 0),
                        "quantity": p.get('quantity', 0),
                        "image_url": image_url,
                        "status": p.get('status', 'غير محدد')
                    })
                
                # الفلترة
                if search_term:
                    term = search_term.lower()
                    all_products = [p for p in all_products if term in p.get('title', '').lower()]
                
                # الترقيم اليدوي (كما اتفقنا)
                per_page = 20
                start = (page - 1) * per_page
                end = start + per_page
                
                return all_products[start:end]
            else:
                logger.error(f"API Error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            return []

    def sync_all_data(self):
        return True
