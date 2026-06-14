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
        self.headers = {
            "Authorization": f"Bearer {os.environ.get('QUMRA_API_KEY', '').strip()}",
            "Content-Type": "application/json"
        }

    def fetch_products(self, search_term="", page=1, per_page=10):
        """جلب المنتجات من الذاكرة المؤقتة مع دعم الترقيم والبحث اللحظي"""
        if not _CACHE["products"] or (time.time() - _CACHE["last_updated"] > CACHE_TIMEOUT):
            self.sync_all_data()
        
        all_data = _CACHE["products"]
        if search_term:
            s = search_term.lower()
            all_data = [p for p in all_data if s in (p.get('title') or "").lower()]
            
        total_items = len(all_data)
        total_pages = (total_items + per_page - 1) // per_page
        
        if page < 1: page = 1
        if page > total_pages and total_pages > 0: page = total_pages
        
        start = (page - 1) * per_page
        products_subset = all_data[start : start + per_page]
        
        return {
            "products": products_subset,
            "total": total_items,
            "page": page,
            "total_pages": total_pages,
            "per_page": per_page
        }

    def sync_all_data(self):
        """جلب كافة المنتجات من النظام السيادي عبر التكرار مع تتبع الأخطاء"""
        all_products = []
        page = 1
        has_more = True
        
        # استعلام GraphQL باستخدام المتغيرات لضمان الاستقرار
        query = """query findAllProducts($page: Int!, $limit: Int!) { 
            findAllProducts(page: $page, limit: $limit) { 
                data { title pricing { price } quantity status images { fileUrl } }
                meta { totalPages }
            } 
        }"""
        
        while has_more:
            variables = {"page": page, "limit": 100}
            
            try:
                response = requests.post(
                    self.endpoint, 
                    json={"query": query, "variables": variables}, 
                    headers=self.headers, 
                    timeout=30
                )
                
                # فحص حالة الاستجابة
                if response.status_code != 200:
                    print(f"❌ API Error Status {response.status_code}: {response.text}")
                    return False
                
                result = response.json().get('data', {}).get('findAllProducts', {})
                items = result.get('data', [])
                
                if not items: break
                
                for p in items:
                    img = p.get('images', [])
                    all_products.append({
                        'title': p.get('title'),
                        'price': p.get('pricing', {}).get('price', 0),
                        'quantity': p.get('quantity', 0),
                        'status': p.get('status'),
                        'image_url': img[0].get('fileUrl') if img else None
                    })
                
                total_pages = result.get('meta', {}).get('totalPages', 1)
                if page >= total_pages:
                    has_more = False
                else:
                    page += 1
                    
            except Exception as e:
                print(f"❌ Sync Exception at page {page}: {str(e)}")
                return False
        
        _CACHE["products"] = all_products
        _CACHE["last_updated"] = time.time()
        return True
