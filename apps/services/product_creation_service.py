# coding: utf-8
# 📂 apps/services/product_creation_service.py

from typing import Dict, List, Optional, Any
from .graphql_client import QomrahGraphQLClient
from .product_media_extras import product_media
from .product_ident_mutation import product_ident


class ProductCreationService:
    """
    خدمة إنشاء المنتجات - متخصصة في عمليات الإنشاء فقط
    تحتوي على: إنشاء منتج، إنشاء مع صور، إنشاء مع SKU تلقائي
    """
    
    def __init__(self):
        self.client = QomrahGraphQLClient()
    
    # ============================================================
    # 📦 CREATE PRODUCT - إنشاء منتج
    # ============================================================
    
    def create_product(self, title: str, description: str = "",
                      price: float = 0.0, status: str = "DRAFT",
                      images: List[str] = None, **kwargs) -> Optional[Dict]:
        """
        إنشاء منتج جديد
        
        Args:
            title: اسم المنتج
            description: وصف المنتج
            price: السعر
            status: الحالة (DRAFT, ACTIVE, INACTIVE, ARCHIVED)
            images: قائمة روابط الصور
            **kwargs: حقول إضافية (sku, weight, dimensions, seo, quantity, tags)
        
        Returns:
            Dict: بيانات المنتج الجديد
        """
        input_data = {
            "title": title,
            "description": description,
            "price": price,
            "status": status
        }
        
        # إضافة صور إن وجدت
        if images:
            input_data["images"] = images
        
        # إضافة حقول إضافية
        optional_fields = ['sku', 'weight', 'dimensions', 'seo', 'quantity', 'tags']
        for field in optional_fields:
            if kwargs.get(field):
                input_data[field] = kwargs[field]
        
        mutation = """
        mutation CreateProduct($input: CreateProductInput!) {
            createProduct(input: $input) {
                id
                qid
                title
                slug
                price
                status
                description
                createdAt
            }
        }
        """
        
        result = self.client.execute_query(mutation, {"input": input_data})
        return result.get('createProduct') if result else None
    
    # ============================================================
    # 📸 CREATE PRODUCT WITH IMAGES - إنشاء منتج مع صور
    # ============================================================
    
    def create_product_with_images(self, title: str, description: str = "",
                                   price: float = 0.0, status: str = "DRAFT",
                                   image_files: List[Dict] = None,
                                   **kwargs) -> Optional[Dict]:
        """
        إنشاء منتج مع رفع الصور أولاً
        
        Args:
            title: اسم المنتج
            description: وصف المنتج
            price: السعر
            status: الحالة
            image_files: قائمة ملفات الصور [{'data': bytes, 'filename': str}]
            **kwargs: حقول إضافية
        
        Returns:
            Dict: بيانات المنتج الجديد مع الصور
        """
        # رفع الصور أولاً
        uploaded_urls = []
        if image_files:
            for img in image_files:
                url = product_media.upload_image(
                    img['data'],
                    img['filename'],
                    img.get('title'),
                    img.get('description')
                )
                if url:
                    uploaded_urls.append(url)
        
        # إنشاء المنتج مع روابط الصور
        return self.create_product(
            title=title,
            description=description,
            price=price,
            status=status,
            images=uploaded_urls,
            **kwargs
        )
    
    # ============================================================
    # 🔢 CREATE PRODUCT WITH AUTO SKU - إنشاء منتج مع SKU تلقائي
    # ============================================================
    
    def create_product_with_auto_sku(self, title: str, description: str = "",
                                     price: float = 0.0, status: str = "DRAFT",
                                     prefix: str = "PRD", **kwargs) -> Optional[Dict]:
        """
        إنشاء منتج مع SKU تلقائي
        
        Args:
            title: اسم المنتج
            description: وصف المنتج
            price: السعر
            status: الحالة
            prefix: بادئة SKU
            **kwargs: حقول إضافية
        
        Returns:
            Dict: بيانات المنتج الجديد
        """
        # إنشاء SKU تلقائي
        sku = product_ident.generate_sku(prefix=prefix)
        
        # إنشاء المنتج مع SKU
        return self.create_product(
            title=title,
            description=description,
            price=price,
            status=status,
            sku=sku,
            **kwargs
        )
    
    # ============================================================
    # 📦 BULK CREATE - إنشاء منتجات متعددة
    # ============================================================
    
    def bulk_create_products(self, products: List[Dict]) -> List[Dict]:
        """
        إنشاء منتجات متعددة دفعة واحدة
        
        Args:
            products: قائمة بيانات المنتجات
        
        Returns:
            List[Dict]: قائمة النتائج {success: bool, qid: str, data: dict, error: str}
        """
        results = []
        
        for idx, product_data in enumerate(products):
            try:
                result = self.create_product(**product_data)
                if result:
                    results.append({
                        'index': idx,
                        'success': True,
                        'qid': result.get('qid'),
                        'data': result
                    })
                else:
                    results.append({
                        'index': idx,
                        'success': False,
                        'error': 'فشل إنشاء المنتج',
                        'data': None
                    })
            except Exception as e:
                results.append({
                    'index': idx,
                    'success': False,
                    'error': str(e),
                    'data': None
                })
        
        return results
    
    # ============================================================
    # 📋 CREATE FROM DICTIONARY - إنشاء من قاموس
    # ============================================================
    
    def create_from_dict(self, data: Dict) -> Optional[Dict]:
        """
        إنشاء منتج من قاموس بيانات
        
        Args:
            data: قاموس يحتوي على جميع بيانات المنتج
        
        Returns:
            Dict: بيانات المنتج الجديد
        """
        # استخراج الحقول الأساسية
        title = data.get('title')
        if not title:
            print("❌ title مطلوب")
            return None
        
        description = data.get('description', '')
        price = data.get('price', 0.0)
        status = data.get('status', 'DRAFT')
        images = data.get('images', [])
        
        # استخراج الحقول الإضافية
        extra_fields = {}
        for field in ['sku', 'weight', 'dimensions', 'seo', 'quantity', 'tags']:
            if field in data:
                extra_fields[field] = data[field]
        
        return self.create_product(
            title=title,
            description=description,
            price=price,
            status=status,
            images=images,
            **extra_fields
        )


# ============================================================
# 🚀 SINGLETON INSTANCE
# ============================================================

product_creator = ProductCreationService()


# ============================================================
# 📋 EXPORTS
# ============================================================

__all__ = [
    'ProductCreationService',
    'product_creator'
]


# ============================================================
# 🧪 TEST
# ============================================================

if __name__ == "__main__":
    service = ProductCreationService()
    
    # ✅ مثال: إنشاء منتج بسيط
    # product = service.create_product(
    #     title="منتج جديد",
    #     description="وصف المنتج",
    #     price=99.99,
    #     status="DRAFT"
    # )
    # print(f"✅ تم إنشاء المنتج: {product}")
    
    # ✅ مثال: إنشاء منتج مع SKU تلقائي
    # product = service.create_product_with_auto_sku(
    #     title="منتج مع SKU تلقائي",
    #     price=149.99,
    #     prefix="PROD"
    # )
    # print(f"✅ تم إنشاء المنتج: {product}")
    
    print("✅ Product Creation Service ready!")
