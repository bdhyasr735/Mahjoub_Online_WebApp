import requests
import os

class QumraSyncManager:
    def __init__(self):
        # الرابط المباشر لـ GraphQL في قمرة
        self.api_url = "https://mahjoub.online/admin/graphql"
        # سيتم جلب التوكن من متغيرات Railway التي أضفتها
        self.token = os.environ.get("QUMRA_API_KEY")

    def fetch_live_products(self, limit=10):
        """جلب البيانات من قمرة للعرض المباشر دون تخزين"""
        if not self.token:
            print("❌ خطأ: QUMRA_API_KEY غير موجود في متغيرات النظام")
            return []

        # الاستعلام المحسن لجلب البيانات مع الصور (Images)
        query = """
        query {
          products(first: %d) {
            data {
              _id
              title
              handle
              images {
                url
              }
              price
            }
          }
        }
        """ % limit
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.api_url, json={'query': query}, headers=headers, timeout=10)
            result = response.json()
            
            # استخراج قائمة المنتجات من استجابة قمرة
            products_list = result.get('data', {}).get('products', {}).get('data', [])
            
            # معالجة بسيطة لضمان وجود رابط صورة افتراضي إذا لم تتوفر صورة
            for p in products_list:
                if p.get('images') and len(p['images']) > 0:
                    p['display_image'] = p['images'][0]['url']
                else:
                    p['display_image'] = "https://via.placeholder.com/150?text=No+Image"
            
            return products_list
            
        except Exception as e:
            print(f"❌ حدث خطأ أثناء جلب البيانات من قمرة: {str(e)}")
            return []

# إنشاء نسخة المحرك ليتم استدعاؤها في الـ Routes
qumra_manager = QumraSyncManager()
