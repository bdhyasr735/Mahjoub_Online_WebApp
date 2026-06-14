# 📂 apps/utils/bridge_engine.py
import requests
from config import Config

class QumraBridgeEngine:
    def __init__(self):
        # الاعتماد على الإعدادات المركزية لضمان الأمان والمرونة
        self.endpoint = Config.QUMRA_API_URL
        self.headers = {
            "Authorization": f"Bearer {Config.QUMRA_API_KEY}",
            "Content-Type": "application/json",
            "apollo-require-preflight": "true"
        }

    def fetch_products_from_qumra(self, search_term=""):
        """
        جلب البيانات مباشرة من قمرة حسب البحث (On-Demand).
        لا يتم تخزين 10 آلاف منتج في الذاكرة لتجنب استهلاك الموارد.
        """
        # استعلام GraphQL مرن يقبل متغير البحث
        query = """
        query($q: String) {
            findAllProducts(filter: { title: $q }) {
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
            # إرسال طلب البحث مباشرة إلى السيرفر السيادي
            response = requests.post(
                self.endpoint, 
                json={"query": query, "variables": {"q": search_term}}, 
                headers=self.headers, 
                timeout=15 # توقيت استجابة سريع لمنع تعليق النظام
            )
            
            if response.status_code == 200:
                result = response.json().get('data', {}).get('findAllProducts', {}).get('data', [])
                
                # معالجة وتنسيق البيانات فور وصولها لتكون جاهزة للعرض
                formatted_products = []
                for p in result:
                    img = p.get('images', [])
                    formatted_products.append({
                        'title': p.get('title', 'بدون عنوان'),
                        'price': p.get('pricing', {}).get('price', 0),
                        'quantity': p.get('quantity', 0),
                        'status': p.get('status', 'N/A'),
                        'image_url': img[0].get('fileUrl') if img and isinstance(img, list) else None
                    })
                return formatted_products
            
            else:
                print(f"❌ API Error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Bridge Exception: {str(e)}")
            return []

    def sync_all_data(self):
        """دالة المزامنة الكاملة (إذا احتاج النظام تحديث الذاكرة)"""
        # يمكن تنفيذ منطق المزامنة هنا إذا كانت هناك حاجة لتحديث قاعدة بيانات محلية
        return True
