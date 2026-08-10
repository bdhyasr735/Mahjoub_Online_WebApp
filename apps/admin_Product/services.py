"""
ProductService: الطبقة البرمجية لإدارة المنتجات والمتغيرات والبحث والربط لقاعدة البيانات وخادم قُمْرا عبر GraphQL
متجر محجوب أونلاين (www.mahjoub.online)
"""

import re
from datetime import datetime

class ProductService:
    """
    خدمة التحكم بالمنتجات، التسعير، المخزون، المتغيرات الديناميكية و SEO
    """
    
    _products_db = [
        {
            "id": "prod_101",
            "title": "هاتف آيفون 15 برو ماكس 256 جيجابايت",
            "slug": "iphone-15-pro-max-256gb",
            "status": "active",
            "description": "هاتف آيفون 15 برو ماكس بأحدث معالج A17 Pro، هيكل من التيتانيوم القوي والفريد، ونظام كاميرات متطور للغاية.",
            "price": 4899.00,
            "compareAtPrice": 5299.00,
            "quantity": 45,
            "sku": "IPH-15PM-256",
            "barcode": "6291048201923",
            "collections": ["الهواتف الذكية", "الإلكترونيات", "أبل"],
            "tags": ["آيفون", "تيتانيوم", "256GB", "A17 Pro"],
            "images": [
                {"fileUrl": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600&auto=format&fit=crop", "isMain": True, "alt": "آيفون 15 برو ماكس"}
            ],
            "seo": {
                "title": "شراء آيفون 15 برو ماكس 256 جيجابايت | محجوب أونلاين",
                "description": "اشترِ آيفون 15 برو ماكس الأصلي بأفضل سعر مع ضمان محجوب أونلاين.",
                "canonicalUrl": "https://www.mahjoub.online/products/iphone-15-pro-max-256gb"
            },
            "dynamic_variants": [
                {"id": "var_1", "name": "اللون: طبيعي تيتانيوم", "price": 4899.00, "quantity": 20, "sku": "IPH15-NAT-256"}
            ],
            "createdAt": "2026-08-01T10:00:00Z",
            "updatedAt": "2026-08-09T14:30:00Z"
        }
    ]

    @classmethod
    def generate_slug(cls, title: str) -> str:
        if not title:
            return ""
        slug = re.sub(r'[^\w\s-]', '', title).strip().lower()
        slug = re.sub(r'[\s_]+', '-', slug)
        return slug or "product-" + str(int(datetime.now().timestamp()))

    @classmethod
    def get_products_page(cls, page: int = 1, per_page: int = 10, search: str = "", status: str = "", collection: str = ""):
        filtered = cls._products_db.copy()

        if search:
            s = search.lower().strip()
            filtered = [
                p for p in filtered
                if s in p['title'].lower() or s in p['slug'].lower() or s in p.get('sku', '').lower()
            ]

        if status and status != 'all':
            filtered = [p for p in filtered if p['status'] == status]

        if collection and collection != 'all':
            filtered = [p for p in filtered if collection in p.get('collections', [])]

        total_items = len(filtered)
        total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 1
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        return {
            "products": filtered[start_idx:end_idx],
            "total_items": total_items,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }

    @classmethod
    def get_product_by_id(cls, product_id: str):
        for p in cls._products_db:
            if p['id'] == product_id:
                return p
        return None

    @classmethod
    def create_product_data(cls, data: dict):
        new_id = f"prod_{int(datetime.now().timestamp())}"
        title = data.get('title', '').strip()
        slug = data.get('slug', '').strip() or cls.generate_slug(title)

        new_product = {
            "id": new_id,
            "title": title,
            "slug": slug,
            "status": data.get('status', 'draft'),
            "description": data.get('description', ''),
            "price": float(data.get('price', 0.0)),
            "compareAtPrice": float(data.get('compareAtPrice', 0.0)) if data.get('compareAtPrice') else None,
            "quantity": int(data.get('quantity', 0)),
            "sku": data.get('sku', ''),
            "barcode": data.get('barcode', ''),
            "collections": data.get('collections', []),
            "tags": data.get('tags', []),
            "images": data.get('images', []),
            "seo": data.get('seo', {}),
            "dynamic_variants": data.get('dynamic_variants', []),
            "createdAt": datetime.now().isoformat() + "Z",
            "updatedAt": datetime.now().isoformat() + "Z"
        }

        cls._products_db.insert(0, new_product)
        return new_product

    @classmethod
    def update_product_data(cls, product_id: str, data: dict):
        product = cls.get_product_by_id(product_id)
        if not product:
            return None

        product['title'] = data.get('title', product['title']).strip()
        product['slug'] = data.get('slug', product['slug']).strip()
        product['status'] = data.get('status', product['status'])
        product['description'] = data.get('description', product['description'])
        product['price'] = float(data.get('price', product['price']))
        product['quantity'] = int(data.get('quantity', product['quantity']))
        product['updatedAt'] = datetime.now().isoformat() + "Z"

        return product

    @classmethod
    def delete_product_data(cls, product_id: str):
        for i, p in enumerate(cls._products_db):
            if p['id'] == product_id:
                deleted = cls._products_db.pop(i)
                return True, deleted
        return False, None

    @classmethod
    def toggle_product_status(cls, product_id: str, new_status: str):
        product = cls.get_product_by_id(product_id)
        if product:
            product['status'] = new_status
            product['updatedAt'] = datetime.now().isoformat() + "Z"
            return True, product
        return False, None

    @classmethod
    def get_collections(cls):
        return ["الهواتف الذكية", "الإلكترونيات", "الساعات الذكية", "الصوتيات", "الأجهزة المنزلية", "عروض محجوب الحصرية"]

    @classmethod
    def get_tags(cls):
        return ["آيفون", "أبل", "سامسونج", "تيتانيوم", "لاسلكي", "ساعة ذكية"]
