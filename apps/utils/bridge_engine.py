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
        جلب المنتجات مع دعم المتغير 'page' لجلب أي صفحة مطلوبة.
        """
        # ملاحظة: أضفنا المتغير (page) للاستعلام إذا كان الـ API يدعمه
        query = """
        query($page: Int) {
            findAllProducts(page: $page) {
                data {
                    title
                    pricing { price }
                    quantity
                    status
                    images { fileUrl }
                }
            }
        }
        """
        
        try:
            # إرسال المتغيرات للـ API
            response = requests.post(
                self.endpoint, 
                json={"query": query, "variables": {"page": page}}, 
                headers=self.headers, 
                timeout=15
            )
            
            if response.status_code == 200:
                full_json = response.json()
                raw_data = full_json.get('data', {}).get('findAllProducts', {}).get('data', [])
                
                processed_products = []
                for p in raw_data:
                    images = p.get('images', [])
                    image_url = images[0].get('fileUrl') if images and len(images) > 0 else 'https://via.placeholder.com/150'
                    
                    processed_products.append({
                        "title": p.get('title', 'بدون اسم'),
                        "price": p.get('pricing', {}).get('price', 0),
                        "quantity": p.get('quantity', 0),
                        "image_url": image_url,
                        "status": p.get('status', 'غير محدد')
                    })
                
                # الفلترة لا تزال تعمل على مستوى الصفحة المجلوبة
                if search_term:
                    term = search_term.lower()
                    processed_products = [p for p in processed_products if term in p.get('title', '').lower()]
                
                return processed_products
            else:
                logger.error(f"API Error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            return []
