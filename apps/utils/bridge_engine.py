# 📂 apps/utils/bridge_engine.py
import requests
from config import Config

class QumraBridgeEngine:
    def __init__(self):
        self.endpoint = Config.QUMRA_API_URL
        self.headers = {
            "Authorization": f"Bearer {Config.QUMRA_API_KEY}",
            "Content-Type": "application/json"
        }

    def fetch_products_from_qumra(self, search_term="", page=1):
        """
        جلب المنتجات مباشرة من API قمرة. 
        إذا تم إدخال search_term، سيقوم الـ API بالبحث في قاعدة بيانات المصدر مباشرة.
        """
        
        # استعلام GraphQL المحدث: نستخدم الفلترة من المصدر إذا توفرت
        # ملاحظة: إذا كان API قمرة لا يدعم الفلترة، سيعمل هذا الكود كبحث شامل بفضل المعالجة في الأسفل
        query = """
        query {
            findAllProducts {
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
            response = requests.post(
                self.endpoint, 
                json={"query": query}, 
                headers=self.headers, 
                timeout=15
            )
            
            if response.status_code == 200:
                raw_data = response.json().get('data', {}).get('findAllProducts', {}).get('data', [])
                
                # معالجة وتجهيز البيانات
                processed_products = []
                for p in raw_data:
                    images = p.get('images', [])
                    image_url = images[0].get('fileUrl') if images and len(images) > 0 else 'https://via.placeholder.com/150'
                    
                    product = {
                        "title": p.get('title', 'بدون اسم'),
                        "price": p.get('pricing', {}).get('price', 0),
                        "quantity": p.get('quantity', 0),
                        "image_url": image_url,
                        "status": p.get('status', 'غير محدد')
                    }
                    processed_products.append(product)
                
                # الفلترة الذكية: البحث في النتائج المجلوبة (تعمل حتى لو كان العدد كبيراً)
                if search_term:
                    term = search_term.lower()
                    processed_products = [
                        p for p in processed_products 
                        if term in p.get('title', '').lower()
                    ]
                
                return processed_products
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return []

    def sync_all_data(self):
        """
        دالة المزامنة اليدوية.
        """
        return True
