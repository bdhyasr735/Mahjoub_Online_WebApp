# coding: utf-8
# 📂 apps/services/update_product_data.py

from typing import Dict, List, Optional, Any
from .graphql_client import QomrahGraphQLClient


# ============================================================
# 📋 MUTATIONS - تحويرات تحديث المنتجات
# ============================================================

# 1️⃣ تحديث المعلومات الأساسية
UPDATE_PRODUCT_INFO_MUTATION = """
mutation UpdateProductInfo($qid: String!, $input: UpdateProductInfoInput!) {
    updateProductInfo(qid: $qid, input: $input) {
        id
        qid
        title
        slug
        description
        status
        updatedAt
    }
}
"""

# 2️⃣ تحديث حالة المنتج
UPDATE_PRODUCT_STATUS_MUTATION = """
mutation UpdateProductStatus($qid: String!, $status: String!) {
    updateProductStatus(qid: $qid, status: $status) {
        id
        qid
        status
        publishedAt
        updatedAt
    }
}
"""

# 3️⃣ تحديث تسعير المنتج
UPDATE_PRODUCT_PRICING_MUTATION = """
mutation UpdateProductPricing($qid: String!, $price: Float!, $compareAtPrice: Float) {
    updateProductPricing(qid: $qid, price: $price, compareAtPrice: $compareAtPrice) {
        id
        qid
        price
        compareAtPrice
        updatedAt
    }
}
"""

# 4️⃣ تحديث أبعاد المنتج
UPDATE_PRODUCT_DIMENSIONS_MUTATION = """
mutation UpdateProductDimensions($qid: String!, $dimensions: DimensionsInput!) {
    updateProductDimensions(qid: $qid, dimensions: $dimensions) {
        id
        qid
        dimensions {
            length
            width
            height
            unit
        }
        updatedAt
    }
}
"""

# 5️⃣ تحديث وزن المنتج
UPDATE_PRODUCT_WEIGHT_MUTATION = """
mutation UpdateProductWeight($qid: String!, $weight: Float!, $unit: String) {
    updateProductWeight(qid: $qid, weight: $weight, unit: $unit) {
        id
        qid
        weight
        unit
        updatedAt
    }
}
"""

# 6️⃣ تحديث تعريف المنتج (SKU, Barcode, etc.)
UPDATE_PRODUCT_IDENTIFICATION_MUTATION = """
mutation UpdateProductIdentification($qid: String!, $identification: IdentificationInput!) {
    updateProductIdentification(qid: $qid, identification: $identification) {
        id
        qid
        identification {
            sku
            barcode
            barcodeType
            hsCode
            countryOfOrigin
            mpn
        }
        updatedAt
    }
}
"""

# 7️⃣ تحديث وصف المنتج
UPDATE_PRODUCT_DESCRIPTION_MUTATION = """
mutation UpdateProductDescription($qid: String!, $description: String!) {
    updateProductDescription(qid: $qid, description: $description) {
        id
        qid
        description
        updatedAt
    }
}
"""

# 8️⃣ تحديث SEO للمنتج
UPDATE_PRODUCT_SEO_MUTATION = """
mutation UpdateProductSEO($qid: String!, $seo: SEOInput!) {
    updateProductSEO(qid: $qid, seo: $seo) {
        id
        qid
        seo {
            title
            description
            keywords
            image
            canonicalUrl
        }
        updatedAt
    }
}
"""

# 9️⃣ تحديث صور المنتج (استبدال كامل)
UPDATE_PRODUCT_IMAGES_MUTATION = """
mutation UpdateProductImages($qid: String!, $images: [String!]!) {
    updateProductImages(qid: $qid, images: $images) {
        id
        qid
        images
        updatedAt
    }
}
"""

# 🔟 تحديث صور المنتج (إضافة/حذف)
UPDATE_PRODUCT_IMAGES_ADVANCED_MUTATION = """
mutation UpdateProductImagesAdvanced($qid: String!, $newImages: [String!]!, $removedImages: [String!]) {
    updateProductImagesAdvanced(qid: $qid, newImages: $newImages, removedImages: $removedImages) {
        id
        qid
        images
        updatedAt
    }
}
"""

# 1️⃣1️⃣ تحديث مجموعات المنتج
UPDATE_PRODUCT_COLLECTION_MUTATION = """
mutation UpdateProductCollection($qid: String!, $collectionQids: [String!]!) {
    updateProductCollection(qid: $qid, collectionQids: $collectionQids) {
        id
        qid
        collections {
            id
            qid
            title
            slug
        }
        updatedAt
    }
}
"""

# 1️⃣2️⃣ تحديث فاريانتات المنتج (دفعة واحدة)
UPDATE_PRODUCT_VARIANTS_MUTATION = """
mutation UpdateProductVariants($qid: String!, $variants: [VariantInput!]!) {
    updateProductVariants(qid: $qid, variants: $variants) {
        id
        qid
        variants {
            id
            qid
            price
            quantity
            sku
            updatedAt
        }
        updatedAt
    }
}
"""

# 1️⃣3️⃣ تحديث فاريانتات المنتج (تحديث فردي)
UPDATE_VARIANT_PRICING_MUTATION = """
mutation UpdateVariantPricing($variantQid: String!, $price: Float!, $compareAtPrice: Float) {
    updateVariantPricing(variantQid: $variantQid, price: $price, compareAtPrice: $compareAtPrice) {
        id
        qid
        price
        compareAtPrice
        updatedAt
    }
}
"""

# 1️⃣4️⃣ تحديث وسائط الفاريانت
UPDATE_VARIANT_MEDIA_MUTATION = """
mutation UpdateVariantMedia($variantQid: String!, $media: [String!]!) {
    updateVariantMedia(variantQid: $variantQid, media: $media) {
        id
        qid
        media
        updatedAt
    }
}
"""

# 1️⃣5️⃣ تحديث كمية الفاريانت
UPDATE_VARIANT_QUANTITY_MUTATION = """
mutation UpdateVariantQuantity($variantQid: String!, $quantity: Int!) {
    updateVariantQuantity(variantQid: $variantQid, quantity: $quantity) {
        id
        qid
        quantity
        updatedAt
    }
}
"""

# 1️⃣6️⃣ حذف فاريانت
REMOVE_VARIANT_MUTATION = """
mutation RemoveVariant($variantQid: String!) {
    removeVariantById(variantQid: $variantQid)
}
"""

# 1️⃣7️⃣ تحديث فاريانتات متعددة دفعة واحدة
BULK_VARIANT_UPDATE_MUTATION = """
mutation BulkVariantUpdate($variants: [VariantUpdateInput!]!) {
    bulkVariantUpdate(variants: $variants) {
        id
        qid
        price
        quantity
        updatedAt
    }
}
"""

# 1️⃣8️⃣ تحديث حالة منتجات متعددة
BULK_UPDATE_PRODUCTS_STATUS_MUTATION = """
mutation BulkUpdateProductsStatus($qids: [String!]!, $status: String!) {
    bulkUpdateProductsStatus(qids: $qids, status: $status) {
        id
        qid
        status
        updatedAt
    }
}
"""

# 1️⃣9️⃣ حذف منتج
DELETE_PRODUCT_MUTATION = """
mutation DeleteProduct($qid: String!) {
    deleteProduct(qid: $qid)
}
"""

# 2️⃣0️⃣ حذف منتجات متعددة
BULK_DELETE_PRODUCTS_MUTATION = """
mutation BulkDeleteProduct($qids: [String!]!) {
    bulkDeleteProduct(qids: $qids)
}
"""

# 2️⃣1️⃣ إنشاء منتج
CREATE_PRODUCT_MUTATION = """
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

# 2️⃣2️⃣ التحقق من توفر الـ Slug
CHECK_PRODUCT_SLUG_MUTATION = """
mutation CheckProductSlug($slug: String!) {
    checkProductSlug(slug: $slug) {
        success
        message
        available
    }
}
"""

# 2️⃣3️⃣ تحديث كامل للمنتج (جميع الحقول دفعة واحدة)
UPDATE_PRODUCT_COMPLETE_MUTATION = """
mutation UpdateProductComplete($qid: String!, $input: UpdateProductCompleteInput!) {
    updateProductComplete(qid: $qid, input: $input) {
        id
        qid
        title
        slug
        description
        status
        price
        compareAtPrice
        weight
        dimensions {
            length
            width
            height
            unit
        }
        identification {
            sku
            barcode
            barcodeType
            hsCode
            countryOfOrigin
            mpn
        }
        images
        collections {
            id
            qid
            title
        }
        seo {
            title
            description
            keywords
            image
            canonicalUrl
        }
        variants {
            id
            qid
            price
            quantity
            sku
        }
        updatedAt
    }
}
"""


# ============================================================
# 🚀 SERVICE CLASS - خدمة تحديث المنتجات
# ============================================================

class ProductUpdateService:
    """
    خدمة تحديث المنتجات
    تحتوي على جميع عمليات التحديث للمنتجات والفاريانتات
    """
    
    def __init__(self):
        self.client = QomrahGraphQLClient()
    
    # ============================================================
    # 📝 PRODUCT UPDATES - تحديثات المنتج
    # ============================================================
    
    def update_product_info(self, qid: str, title: str = None,
                           description: str = None, status: str = None,
                           **kwargs) -> Optional[Dict]:
        """
        تحديث معلومات المنتج الأساسية
        
        Args:
            qid: معرف المنتج
            title: الاسم الجديد (اختياري)
            description: الوصف الجديد (اختياري)
            status: الحالة الجديدة (اختياري)
            **kwargs: حقول إضافية (slug, tags, etc.)
        
        Returns:
            Dict: بيانات المنتج المحدث
        """
        input_data = {}
        if title is not None:
            input_data["title"] = title
        if description is not None:
            input_data["description"] = description
        if status is not None:
            input_data["status"] = status
        if kwargs.get('slug'):
            input_data["slug"] = kwargs.get('slug')
        if kwargs.get('tags'):
            input_data["tags"] = kwargs.get('tags')
        
        if not input_data:
            print("⚠️ لا توجد بيانات للتحديث")
            return None
        
        result = self.client.execute_query(
            UPDATE_PRODUCT_INFO_MUTATION,
            {"qid": qid, "input": input_data}
        )
        return result.get('updateProductInfo') if result else None
    
    def update_product_status(self, qid: str, status: str) -> Optional[Dict]:
        """
        تحديث حالة المنتج
        
        Args:
            qid: معرف المنتج
            status: الحالة الجديدة (ACTIVE, INACTIVE, DRAFT, ARCHIVED)
        
        Returns:
            Dict: بيانات الحالة المحدثة
        """
        result = self.client.execute_query(
            UPDATE_PRODUCT_STATUS_MUTATION,
            {"qid": qid, "status": status}
        )
        return result.get('updateProductStatus') if result else None
    
    def update_product_pricing(self, qid: str, price: float,
                              compare_at_price: float = None) -> Optional[Dict]:
        """
        تحديث تسعير المنتج
        
        Args:
            qid: معرف المنتج
            price: السعر الجديد
            compare_at_price: السعر المقارن (اختياري)
        
        Returns:
            Dict: بيانات التسعير المحدثة
        """
        variables = {"qid": qid, "price": price}
        if compare_at_price is not None:
            variables["compareAtPrice"] = compare_at_price
        
        result = self.client.execute_query(UPDATE_PRODUCT_PRICING_MUTATION, variables)
        return result.get('updateProductPricing') if result else None
    
    def update_product_dimensions(self, qid: str, length: float,
                                 width: float, height: float,
                                 unit: str = 'cm') -> Optional[Dict]:
        """
        تحديث أبعاد المنتج
        
        Args:
            qid: معرف المنتج
            length: الطول
            width: العرض
            height: الارتفاع
            unit: الوحدة (cm, m, in)
        
        Returns:
            Dict: بيانات الأبعاد المحدثة
        """
        dimensions = {
            "length": length,
            "width": width,
            "height": height,
            "unit": unit
        }
        result = self.client.execute_query(
            UPDATE_PRODUCT_DIMENSIONS_MUTATION,
            {"qid": qid, "dimensions": dimensions}
        )
        return result.get('updateProductDimensions') if result else None
    
    def update_product_weight(self, qid: str, weight: float,
                             unit: str = 'kg') -> Optional[Dict]:
        """
        تحديث وزن المنتج
        
        Args:
            qid: معرف المنتج
            weight: الوزن
            unit: الوحدة (kg, g, lb, oz)
        
        Returns:
            Dict: بيانات الوزن المحدثة
        """
        result = self.client.execute_query(
            UPDATE_PRODUCT_WEIGHT_MUTATION,
            {"qid": qid, "weight": weight, "unit": unit}
        )
        return result.get('updateProductWeight') if result else None
    
    def update_product_identification(self, qid: str, sku: str = None,
                                     barcode: str = None,
                                     barcode_type: str = None,
                                     hs_code: str = None,
                                     country_of_origin: str = None,
                                     mpn: str = None) -> Optional[Dict]:
        """
        تحديث بيانات تعريف المنتج
        
        Args:
            qid: معرف المنتج
            sku: رقم SKU
            barcode: الباركود
            barcode_type: نوع الباركود
            hs_code: رمز HS
            country_of_origin: بلد المنشأ
            mpn: رقم MPN
        
        Returns:
            Dict: بيانات التعريف المحدثة
        """
        identification = {}
        if sku is not None:
            identification["sku"] = sku
        if barcode is not None:
            identification["barcode"] = barcode
        if barcode_type is not None:
            identification["barcodeType"] = barcode_type
        if hs_code is not None:
            identification["hsCode"] = hs_code
        if country_of_origin is not None:
            identification["countryOfOrigin"] = country_of_origin
        if mpn is not None:
            identification["mpn"] = mpn
        
        if not identification:
            print("⚠️ لا توجد بيانات تعريف للتحديث")
            return None
        
        result = self.client.execute_query(
            UPDATE_PRODUCT_IDENTIFICATION_MUTATION,
            {"qid": qid, "identification": identification}
        )
        return result.get('updateProductIdentification') if result else None
    
    def update_product_description(self, qid: str, description: str) -> Optional[Dict]:
        """
        تحديث وصف المنتج
        
        Args:
            qid: معرف المنتج
            description: النص الجديد للوصف
        
        Returns:
            Dict: بيانات الوصف المحدثة
        """
        result = self.client.execute_query(
            UPDATE_PRODUCT_DESCRIPTION_MUTATION,
            {"qid": qid, "description": description}
        )
        return result.get('updateProductDescription') if result else None
    
    def update_product_seo(self, qid: str, title: str = None,
                          description: str = None, keywords: str = None,
                          image: str = None, canonical_url: str = None) -> Optional[Dict]:
        """
        تحديث SEO للمنتج
        
        Args:
            qid: معرف المنتج
            title: عنوان SEO
            description: وصف SEO
            keywords: كلمات مفتاحية
            image: صورة SEO
            canonical_url: الرابط الأساسي
        
        Returns:
            Dict: بيانات SEO المحدثة
        """
        seo = {}
        if title is not None:
            seo["title"] = title
        if description is not None:
            seo["description"] = description
        if keywords is not None:
            seo["keywords"] = keywords
        if image is not None:
            seo["image"] = image
        if canonical_url is not None:
            seo["canonicalUrl"] = canonical_url
        
        if not seo:
            print("⚠️ لا توجد بيانات SEO للتحديث")
            return None
        
        result = self.client.execute_query(
            UPDATE_PRODUCT_SEO_MUTATION,
            {"qid": qid, "seo": seo}
        )
        return result.get('updateProductSEO') if result else None
    
    def update_product_images(self, qid: str, images: List[str]) -> Optional[Dict]:
        """
        تحديث صور المنتج (استبدال كامل)
        
        Args:
            qid: معرف المنتج
            images: قائمة روابط الصور الجديدة
        
        Returns:
            Dict: بيانات الصور المحدثة
        """
        result = self.client.execute_query(
            UPDATE_PRODUCT_IMAGES_MUTATION,
            {"qid": qid, "images": images}
        )
        return result.get('updateProductImages') if result else None
    
    def update_product_images_advanced(self, qid: str,
                                      new_images: List[str],
                                      removed_images: List[str] = None) -> Optional[Dict]:
        """
        تحديث صور المنتج (إضافة وحذف)
        
        Args:
            qid: معرف المنتج
            new_images: قائمة الصور الجديدة للإضافة
            removed_images: قائمة الصور للحذف
        
        Returns:
            Dict: بيانات الصور المحدثة
        """
        result = self.client.execute_query(
            UPDATE_PRODUCT_IMAGES_ADVANCED_MUTATION,
            {"qid": qid, "newImages": new_images, "removedImages": removed_images or []}
        )
        return result.get('updateProductImagesAdvanced') if result else None
    
    def update_product_collection(self, qid: str,
                                 collection_qids: List[str]) -> Optional[Dict]:
        """
        تحديث مجموعات المنتج
        
        Args:
            qid: معرف المنتج
            collection_qids: قائمة معرفات المجموعات
        
        Returns:
            Dict: بيانات المجموعات المحدثة
        """
        result = self.client.execute_query(
            UPDATE_PRODUCT_COLLECTION_MUTATION,
            {"qid": qid, "collectionQids": collection_qids}
        )
        return result.get('updateProductCollection') if result else None
    
    def update_product_variants(self, qid: str,
                               variants: List[Dict]) -> Optional[Dict]:
        """
        تحديث فاريانتات المنتج (دفعة واحدة)
        
        Args:
            qid: معرف المنتج
            variants: قائمة بيانات الفاريانتات
        
        Returns:
            Dict: بيانات الفاريانتات المحدثة
        """
        result = self.client.execute_query(
            UPDATE_PRODUCT_VARIANTS_MUTATION,
            {"qid": qid, "variants": variants}
        )
        return result.get('updateProductVariants') if result else None
    
    def update_product_complete(self, qid: str, input_data: Dict) -> Optional[Dict]:
        """
        تحديث كامل للمنتج (جميع الحقول دفعة واحدة)
        
        Args:
            qid: معرف المنتج
            input_data: جميع بيانات التحديث
        
        Returns:
            Dict: بيانات المنتج المحدثة
        """
        result = self.client.execute_query(
            UPDATE_PRODUCT_COMPLETE_MUTATION,
            {"qid": qid, "input": input_data}
        )
        return result.get('updateProductComplete') if result else None
    
    # ============================================================
    # 🎨 VARIANT UPDATES - تحديثات الفاريانتات
    # ============================================================
    
    def update_variant_pricing(self, variant_qid: str, price: float,
                              compare_at_price: float = None) -> Optional[Dict]:
        """
        تحديث تسعير الفاريانت
        
        Args:
            variant_qid: معرف الفاريانت
            price: السعر الجديد
            compare_at_price: السعر المقارن (اختياري)
        
        Returns:
            Dict: بيانات التسعير المحدثة
        """
        variables = {"variantQid": variant_qid, "price": price}
        if compare_at_price is not None:
            variables["compareAtPrice"] = compare_at_price
        
        result = self.client.execute_query(UPDATE_VARIANT_PRICING_MUTATION, variables)
        return result.get('updateVariantPricing') if result else None
    
    def update_variant_media(self, variant_qid: str, media: List[str]) -> Optional[Dict]:
        """
        تحديث وسائط الفاريانت
        
        Args:
            variant_qid: معرف الفاريانت
            media: قائمة روابط الوسائط
        
        Returns:
            Dict: بيانات الوسائط المحدثة
        """
        result = self.client.execute_query(
            UPDATE_VARIANT_MEDIA_MUTATION,
            {"variantQid": variant_qid, "media": media}
        )
        return result.get('updateVariantMedia') if result else None
    
    def update_variant_quantity(self, variant_qid: str, quantity: int) -> Optional[Dict]:
        """
        تحديث كمية الفاريانت
        
        Args:
            variant_qid: معرف الفاريانت
            quantity: الكمية الجديدة
        
        Returns:
            Dict: بيانات الكمية المحدثة
        """
        result = self.client.execute_query(
            UPDATE_VARIANT_QUANTITY_MUTATION,
            {"variantQid": variant_qid, "quantity": quantity}
        )
        return result.get('updateVariantQuantity') if result else None
    
    def remove_variant(self, variant_qid: str) -> bool:
        """
        حذف فاريانت
        
        Args:
            variant_qid: معرف الفاريانت
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        result = self.client.execute_query(REMOVE_VARIANT_MUTATION, {"variantQid": variant_qid})
        return result.get('removeVariantById', False) if result else False
    
    def bulk_variant_update(self, variants: List[Dict]) -> Optional[List[Dict]]:
        """
        تحديث فاريانتات متعددة دفعة واحدة
        
        Args:
            variants: قائمة بيانات الفاريانتات
        
        Returns:
            List[Dict]: قائمة الفاريانتات المحدثة
        """
        result = self.client.execute_query(BULK_VARIANT_UPDATE_MUTATION, {"variants": variants})
        return result.get('bulkVariantUpdate', []) if result else []
    
    # ============================================================
    # 🗑️ DELETE OPERATIONS - عمليات الحذف
    # ============================================================
    
    def delete_product(self, qid: str) -> bool:
        """
        حذف منتج
        
        Args:
            qid: معرف المنتج
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        result = self.client.execute_query(DELETE_PRODUCT_MUTATION, {"qid": qid})
        return result.get('deleteProduct', False) if result else False
    
    def bulk_delete_products(self, qids: List[str]) -> bool:
        """
        حذف منتجات متعددة
        
        Args:
            qids: قائمة معرفات المنتجات
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        result = self.client.execute_query(BULK_DELETE_PRODUCTS_MUTATION, {"qids": qids})
        return result.get('bulkDeleteProduct', False) if result else False
    
    def bulk_update_products_status(self, qids: List[str], status: str) -> Optional[List[Dict]]:
        """
        تحديث حالة منتجات متعددة
        
        Args:
            qids: قائمة معرفات المنتجات
            status: الحالة الجديدة
        
        Returns:
            List[Dict]: قائمة المنتجات المحدثة
        """
        result = self.client.execute_query(
            BULK_UPDATE_PRODUCTS_STATUS_MUTATION,
            {"qids": qids, "status": status}
        )
        return result.get('bulkUpdateProductsStatus', []) if result else []
    
    # ============================================================
    # ✏️ CREATE OPERATIONS - عمليات الإنشاء
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
            **kwargs: حقول إضافية (sku, weight, dimensions, seo, etc.)
        
        Returns:
            Dict: بيانات المنتج الجديد
        """
        input_data = {
            "title": title,
            "description": description,
            "price": price,
            "status": status
        }
        
        if images:
            input_data["images"] = images
        if kwargs.get('sku'):
            input_data["sku"] = kwargs.get('sku')
        if kwargs.get('weight'):
            input_data["weight"] = kwargs.get('weight')
        if kwargs.get('dimensions'):
            input_data["dimensions"] = kwargs.get('dimensions')
        if kwargs.get('seo'):
            input_data["seo"] = kwargs.get('seo')
        if kwargs.get('quantity'):
            input_data["quantity"] = kwargs.get('quantity')
        if kwargs.get('tags'):
            input_data["tags"] = kwargs.get('tags')
        
        result = self.client.execute_query(CREATE_PRODUCT_MUTATION, {"input": input_data})
        return result.get('createProduct') if result else None
    
    def check_product_slug(self, slug: str) -> Dict:
        """
        التحقق من توفر الـ Slug
        
        Args:
            slug: الاسم المختصر للتحقق
        
        Returns:
            Dict: {success, message, available}
        """
        result = self.client.execute_query(CHECK_PRODUCT_SLUG_MUTATION, {"slug": slug})
        return result.get('checkProductSlug', {}) if result else {}
    
    # ============================================================
    # 🔄 COMPLETE SYNC - مزامنة كاملة
    # ============================================================
    
    def sync_product_complete(self, qid: str, data: Dict) -> bool:
        """
        مزامنة كاملة للمنتج (جميع الحقول)
        
        Args:
            qid: معرف المنتج
            data: جميع بيانات المنتج
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        try:
            success = True
            
            # تحديث المعلومات الأساسية
            if 'title' in data or 'description' in data or 'status' in data:
                info = {}
                if 'title' in data:
                    info['title'] = data['title']
                if 'description' in data:
                    info['description'] = data['description']
                if 'status' in data:
                    info['status'] = data['status']
                if 'slug' in data:
                    info['slug'] = data['slug']
                if 'tags' in data:
                    info['tags'] = data['tags']
                if info:
                    if not self.update_product_info(qid, **info):
                        success = False
            
            # تحديث السعر
            if 'price' in data:
                if not self.update_product_pricing(qid, data['price'], data.get('compare_at_price')):
                    success = False
            
            # تحديث الصور
            if 'images' in data:
                if not self.update_product_images(qid, data['images']):
                    success = False
            
            # تحديث الأبعاد
            if 'dimensions' in data:
                dims = data['dimensions']
                if not self.update_product_dimensions(qid, dims['length'], dims['width'], dims['height'], dims.get('unit', 'cm')):
                    success = False
            
            # تحديث الوزن
            if 'weight' in data:
                if not self.update_product_weight(qid, data['weight'], data.get('weight_unit', 'kg')):
                    success = False
            
            # تحديث التعريف
            if 'sku' in data or 'barcode' in data:
                ident = {}
                if 'sku' in data:
                    ident['sku'] = data['sku']
                if 'barcode' in data:
                    ident['barcode'] = data['barcode']
                if 'barcode_type' in data:
                    ident['barcodeType'] = data['barcode_type']
                if 'hs_code' in data:
                    ident['hsCode'] = data['hs_code']
                if 'country_of_origin' in data:
                    ident['countryOfOrigin'] = data['country_of_origin']
                if 'mpn' in data:
                    ident['mpn'] = data['mpn']
                if ident:
                    if not self.update_product_identification(qid, **ident):
                        success = False
            
            # تحديث SEO
            if 'seo' in data:
                if not self.update_product_seo(qid, **data['seo']):
                    success = False
            
            # تحديث المجموعات
            if 'collections' in data:
                if not self.update_product_collection(qid, data['collections']):
                    success = False
            
            # تحديث الفاريانتات
            if 'variants' in data:
                if not self.update_product_variants(qid, data['variants']):
                    success = False
            
            return success
            
        except Exception as e:
            print(f"❌ خطأ في sync_product_complete: {e}")
            return False


# ============================================================
# 🚀 SINGLETON INSTANCE
# ============================================================

product_update = ProductUpdateService()


# ============================================================
# 📋 EXPORTS - للاستخدام المباشر
# ============================================================

__all__ = [
    'UPDATE_PRODUCT_INFO_MUTATION',
    'UPDATE_PRODUCT_STATUS_MUTATION',
    'UPDATE_PRODUCT_PRICING_MUTATION',
    'UPDATE_PRODUCT_DIMENSIONS_MUTATION',
    'UPDATE_PRODUCT_WEIGHT_MUTATION',
    'UPDATE_PRODUCT_IDENTIFICATION_MUTATION',
    'UPDATE_PRODUCT_DESCRIPTION_MUTATION',
    'UPDATE_PRODUCT_SEO_MUTATION',
    'UPDATE_PRODUCT_IMAGES_MUTATION',
    'UPDATE_PRODUCT_IMAGES_ADVANCED_MUTATION',
    'UPDATE_PRODUCT_COLLECTION_MUTATION',
    'UPDATE_PRODUCT_VARIANTS_MUTATION',
    'UPDATE_VARIANT_PRICING_MUTATION',
    'UPDATE_VARIANT_MEDIA_MUTATION',
    'UPDATE_VARIANT_QUANTITY_MUTATION',
    'REMOVE_VARIANT_MUTATION',
    'BULK_VARIANT_UPDATE_MUTATION',
    'BULK_UPDATE_PRODUCTS_STATUS_MUTATION',
    'DELETE_PRODUCT_MUTATION',
    'BULK_DELETE_PRODUCTS_MUTATION',
    'CREATE_PRODUCT_MUTATION',
    'CHECK_PRODUCT_SLUG_MUTATION',
    'UPDATE_PRODUCT_COMPLETE_MUTATION',
    'ProductUpdateService',
    'product_update'
]


# ============================================================
# 🧪 TEST - اختبار سريع (اختياري)
# ============================================================

if __name__ == "__main__":
    service = ProductUpdateService()
    
    # مثال: إنشاء منتج جديد
    # product = service.create_product(
    #     title="منتج جديد",
    #     description="وصف المنتج",
    #     price=99.99,
    #     status="DRAFT"
    # )
    # print(f"✅ تم إنشاء المنتج: {product}")
    
    print("✅ Product Update Service ready!")
