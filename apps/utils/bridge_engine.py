# coding: utf-8
# 📂 apps/utils/bridge_engine.py

import requests
import os

class QumraBridgeEngine:
    def __init__(self):
        self.endpoint = "https://mahjoub.online/admin/graphql"
        api_token = os.environ.get('QUMRA_API_KEY', '').strip()
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def execute_query(self, query, variables=None):
        payload = {"query": query, "variables": variables or {}}
        try:
            response = requests.post(self.endpoint, json=payload, headers=self.headers, timeout=20)
            return response.json()
        except Exception as e:
            print(f"⚠️ Connection Error: {e}")
            return {}

    def fetch_products(self, search_term="", page=1):
        """
        جلب المنتجات باستخدام استعلام بسيط وتصفية النتائج برمجياً محلياً.
        """
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
        # نرسل الاستعلام بدون متغيرات لتجنب خطأ الـ GraphQL
        result = self.execute_query(query)
        
        # استخراج القائمة الكاملة من السيرفر
        all_products = result.get('data', {}).get('findAllProducts', {}).get('data', [])
        
        # 1. التصفية المحلية بناءً على نص البحث
        if search_term:
            search_term = search_term.lower()
            all_products = [p for p in all_products if search_term in (p.get('title') or "").lower()]
            
        # 2. الترقيم المحلي (Local Pagination)
        per_page = 16
        total_products = len(all_products)
        start = (page - 1) * per_page
        end = start + per_page
        products = all_products[start:end]
        
        # 3. معالجة البيانات وتجهيزها للعرض
        processed_products = []
        for p in products:
            pricing = p.get('pricing') or {}
            images = p.get('images') or []
            img_url = images[0].get('fileUrl') if images and isinstance(images, list) else None
            
            processed_products.append({
                'title': p.get('title'),
                'price': pricing.get('price', 0),
                'quantity': p.get('quantity', 0),
                'status': p.get('status'),
                'image_url': img_url
            })
            
        return processed_products
