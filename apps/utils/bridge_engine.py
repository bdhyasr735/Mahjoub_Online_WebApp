# coding: utf-8
# 📂 apps/utils/bridge_engine.py - محرك المزامنة السيادي

import requests
from config import Config

class QumraBridgeEngine:
    def __init__(self):
        self.endpoint = "https://mahjoub.online/admin/graphql"
        # استرجاع الـ API Key من إعدادات البيئة
        api_token = getattr(Config, 'QUMRA_API_KEY', '') or ""
        self.headers = {
            "Authorization": f"Bearer {api_token.strip()}",
            "Content-Type": "application/json",
            "apollo-require-preflight": "true" 
        }

    def execute_query(self, query, variables=None):
        """تنفيذ استعلام GraphQL وإرجاع البيانات بشكل آمن."""
        payload = {"query": query, "variables": variables or {}}
        try:
            response = requests.post(self.endpoint, json=payload, headers=self.headers, timeout=15)
            response.raise_for_status()
            result = response.json()
            # التأكد من عدم وجود أخطاء في استجابة GraphQL نفسها
            if 'errors' in result:
                print(f"⚠️ GraphQL Errors: {result['errors']}")
            return result.get('data', {})
        except Exception as e:
            print(f"⚠️ Bridge Engine Connection Error: {e}")
            return {}

    def fetch_latest_products(self, limit=10, page=1):
        """جلب المنتجات وتجهيز القوالب التلقائية دون تخزين إضافي في القاعدة."""
        query = """
        query GetProducts($limit: Int, $page: Int) {
            findAllProducts(input: { limit: $limit, page: $page }) {
                data {
                    title
                    quantity
                    image_url
                    description
                    pricing {
                        price
                    }
                }
            }
        }
        """
        variables = {"limit": limit, "page": page}
        data = self.execute_query(query, variables)
        
        # استخراج البيانات من الهيكل المتداخل
        find_all = data.get('findAllProducts', {})
        products = find_all.get('data', [])
        
        if not products:
            return []
        
        # إضافة "القالب التلقائي" لكل منتج للاستخدام المباشر في القوالب
        for p in products:
            p['auto_template'] = self.generate_product_html(p)
            
        return products if isinstance(products, list) else []

    def generate_product_html(self, product):
        """توليد قالب HTML مصغر للعرض اللحظي."""
        try:
            pricing = product.get('pricing') or {}
            price = pricing.get('price', '0')
            img = product.get('image_url') or 'https://via.placeholder.com/200'
            title = product.get('title', 'منتج بدون اسم')
            
            return f"""
            <div class="product-snippet" style="display:flex; align-items:center; gap:10px;">
                <img src="{img}" style="width:50px; height:50px; object-fit:cover; border-radius:4px;">
                <div style="font-size: 0.8rem;">
                    <strong>{title}</strong><br>
                    <span>{price} ر.س</span>
                </div>
            </div>
            """
        except Exception:
            return '<div class="product-snippet">بيانات المنتج غير مكتملة</div>'
