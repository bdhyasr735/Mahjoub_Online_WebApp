"""
ProductService: الطبقة البرمجية لإدارة المنتجات والمتغيرات والبحث والربط لقاعدة البيانات
متجر محجوب أونلاين (www.mahjoub.online)
"""

import json
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
                {"fileUrl": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600&auto=format&fit=crop", "isMain": True, "alt": "آيفون 15 برو ماكس"},
                {"fileUrl": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&auto=format&fit=crop", "isMain": False, "alt": "شاشة الهاتف"}
            ],
            "seo": {
                "title": "شراء آيفون 15 برو ماكس 256 جيجابايت | محجوب أونلاين",
                "description": "اشترِ آيفون 15 برو ماكس الأصلي بأفضل سعر في المملكة ومصر مع ضمان محجوب أونلاين والشحن السريع.",
                "canonicalUrl": "https://www.mahjoub.online/products/iphone-15-pro-max-256gb"
            },
            "dynamic_variants": [
                {"id": "var_1", "name": "اللون: طبيعي تيتانيوم", "type": "Color", "price": 4899.00, "compareAtPrice": 5299.00, "quantity": 20, "sku": "IPH15-NAT-256", "status": "active"},
                {"id": "var_2", "name": "اللون: أسود تيتانيوم", "type": "Color", "price": 4899.00, "compareAtPrice": 5299.00, "quantity": 15, "sku": "IPH15-BLK-256", "status": "active"},
                {"id": "var_3", "name": "اللون: أزرق تيتانيوم", "type": "Color", "price": 4899.00, "compareAtPrice": 5299.00, "quantity": 10, "sku": "IPH15-BLU-256", "status": "active"}
            ],
            "createdAt": "2026-08-01T10:00:00Z",
            "updatedAt": "2026-08-09T14:30:00Z"
        },
        {
            "id": "prod_102",
            "title": "ساعة ذكية محجوب سبورت برو V2",
            "slug": "mahjoub-sport-pro-v2-watch",
            "status": "active",
            "description": "ساعة رياضية ذكية تتضمن قياس نبضات القلب، نسبة الأكسجين في الدم، مقاومة للماء حتى عمق 50 متراً وبطارية تدوم 14 يوماً.",
            "price": 349.00,
            "compareAtPrice": 499.00,
            "quantity": 120,
            "sku": "M3-WTC-V2",
            "barcode": "6291048201999",
            "collections": ["الساعات الذكية", "الإلكترونيات", "أجهزة لياقة"],
            "tags": ["ساعة ذكية", "محجوب", "لياقة", "مقاومة للماء"],
            "images": [
                {"fileUrl": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop", "isMain": True, "alt": "ساعة محجوب سبورت برو"}
            ],
            "seo": {
                "title": "ساعة ذكية محجوب سبورت برو V2 | متجر محجوب أونلاين",
                "description": "اطلب ساعة محجوب الرياضية V2 الذكية وتتبع تمارينك وصحتك بدقة عالية مع خدمة التوصيل الفوري.",
                "canonicalUrl": "https://www.mahjoub.online/products/mahjoub-sport-pro-v2-watch"
            },
            "dynamic_variants": [
                {"id": "var_10", "name": "الحزام: أسود سيليكون", "type": "Strap", "price": 349.00, "compareAtPrice": 499.00, "quantity": 70, "sku": "WTC-V2-BLK", "status": "active"},
                {"id": "var_11", "name": "الحزام: أورانج رياضي", "type": "Strap", "price": 369.00, "compareAtPrice": 519.00, "quantity": 50, "sku": "WTC-V2-ORG", "status": "active"}
            ],
            "createdAt": "2026-08-03T11:20:00Z",
            "updatedAt": "2026-08-08T09:15:00Z"
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
        paginated_products = filtered[start_idx:end_idx]

        return {
            "products": paginated_products,
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

        variants = data.get('dynamic_variants', [])
        total_qty = data.get('quantity', 0)
        if variants:
            total_qty = sum(int(v.get('quantity', 0)) for v in variants)

        new_product = {
            "id": new_id,
            "title": title,
            "slug": slug,
            "status": data.get('status', 'draft'),
            "description": data.get('description', ''),
            "price": float(data.get('price', 0.0)),
            "compareAtPrice": float(data.get('compareAtPrice', 0.0)) if data.get('compareAtPrice') else None,
            "quantity": int(total_qty),
            "sku": data.get('sku', ''),
            "barcode": data.get('barcode', ''),
            "collections": data.get('collections', []),
            "tags": data.get('tags', []),
            "images": data.get('images', []),
            "seo": {
                "title": data.get('seo', {}).get('title', f"{title} | محجوب أونلاين"),
                "description": data.get('seo', {}).get('description', ''),
                "canonicalUrl": data.get('seo', {}).get('canonicalUrl', f"https://www.mahjoub.online/products/{slug}")
            },
            "dynamic_variants": variants,
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

        title = data.get('title', product['title']).strip()
        slug = data.get('slug', product['slug']).strip() or cls.generate_slug(title)

        variants = data.get('dynamic_variants', product.get('dynamic_variants', []))
        total_qty = data.get('quantity', product.get('quantity', 0))
        if variants:
            total_qty = sum(int(v.get('quantity', 0)) for v in variants)

        product['title'] = title
        product['slug'] = slug
        product['status'] = data.get('status', product['status'])
        product['description'] = data.get('description', product['description'])
        product['price'] = float(data.get('price', product['price']))
        product['compareAtPrice'] = float(data.get('compareAtPrice')) if data.get('compareAtPrice') is not None else product.get('compareAtPrice')
        product['quantity'] = int(total_qty)
        product['sku'] = data.get('sku', product.get('sku', ''))
        product['barcode'] = data.get('barcode', product.get('barcode', ''))
        product['collections'] = data.get('collections', product.get('collections', []))
        product['tags'] = data.get('tags', product.get('tags', []))
        product['images'] = data.get('images', product.get('images', []))
        
        seo_input = data.get('seo', {})
        product['seo'] = {
            "title": seo_input.get('title', product['seo']['title']),
            "description": seo_input.get('description', product['seo']['description']),
            "canonicalUrl": seo_input.get('canonicalUrl', product['seo']['canonicalUrl'])
        }
        product['dynamic_variants'] = variants
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
        return ["الهواتف الذكية", "الإلكترونيات", "الساعات الذكية", "الصوتيات", "الأجهزة المنزلية", "عروض محجوب الحصرية", "أجهزة لياقة", "أكسسوارات"]

    @classmethod
    def get_tags(cls):
        return ["آيفون", "أبل", "سامسونج", "تيتانيوم", "لاسلكي", "ساعة ذكية", "عزل ضوضاء", "شحن سريع"]
