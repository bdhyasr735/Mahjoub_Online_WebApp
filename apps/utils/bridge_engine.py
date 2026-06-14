# coding: utf-8
# 📂 apps/utils/bridge_engine.py

import requests
import os
import time

# ذاكرة مؤقتة للمنتجات
_CACHE = {"products": [], "last_updated": 0}
CACHE_TIMEOUT = 3600  # تحديث تلقائي كل ساعة

class QumraBridgeEngine:
    def __init__(self):
        self.endpoint = "https://mahjoub.online/admin/graphql"
        # التأكد من وجود مفتاح API
        api_key = os.environ.get('QUMRA_API_KEY', '').strip()
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "apollo-require-preflight": "true" 
        }

    def fetch_products(self, search_term="", page=1, per_page=10):
        """جلب المنتجات من الذاكرة المؤقتة مع دعم الترقيم والبحث اللحظي"""
        # تحديث تلقائي إذا انتهت المدة أو كانت الذاكرة فارغة
        if not _CACHE["products"] or (time.time() - _CACHE["last_updated"] > CACHE_TIMEOUT):
            self.sync_all_data()
        
        all_data = _CACHE["products"]
        
        # البحث (Search) - يتم الفلترة على مستوى الذاكرة لسرعة الاستجابة
        if search_term:
            s = search_term.lower()
            all_data = [p for p in all_data if s in (p.get('title') or "").lower()]
            
        # منطق الترقيم (Pagination)
        total_items = len(all_data)
        total_pages = (total_items + per_page - 1) // per_page
        
        # التأكد من نطاق الصفحة
        if page < 1: page = 1
        if page > total_pages and total_pages > 0: page = total_pages
        
        start = (page - 1) * per_page
        products_subset = all_data[start : start + per_page]
        
        return {
            "products": products_subset,
            "total": total_items,
            "page": page,
            "total_pages": total_pages if total_pages > 0 else 1,
            "per_page": per_page
        }

    def sync_all_data(self):
        """جلب كافة المنتجات من النظام السيادي وتحديث الذاكرة المؤقتة"""
        all_products = []
        
        query = """query { 
            findAllProducts { 
                data { 
                    title 
                    pricing { price } 
                    quantity 
                    status 
                    images { fileUrl } 
                }
            } 
        }"""
        
        try:
            response = requests.post(
                self.endpoint, 
                json={"query": query}, 
                headers=self.headers, 
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ API Error Status {response.status_code}: {response.text}")
                return False
            
            # استخراج البيانات بهيكل آمن
            data_response = response.json().get('data', {})
            if not data_response or 'findAllProducts' not in data_response:
                return False
                
            items = data_response.get('findAllProducts', {}).get('data', [])
            
            for p in items:
                img = p.get('images', [])
                # ضمان وجود جميع القيم الافتراضية
                all_products.append({
                    'title': p.get('title', 'بدون عنوان'),
                    'price': p.get('pricing', {}).get('price', 0),
                    'quantity': p.get('quantity', 0),
                    'status': p.get('status', 'N/A'),
                    'image_url': img[0].get('fileUrl') if img and isinstance(img, list) else None
                })
        
        except Exception as e:
            print(f"❌ Sync Exception: {str(e)}")
            return False
        
        _CACHE["products"] = all_products
        _CACHE["last_updated"] = time.time()
        return True
