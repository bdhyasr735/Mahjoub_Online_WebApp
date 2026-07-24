# coding: utf-8
# 📂 apps/services/update_product_data.py
"""
ملف يحتوي على جميع تحويرات (Mutations) تحديث المنتجات
"""

from typing import Dict, List, Optional, Any
from .graphql_client import QomrahGraphQLClient


class ProductUpdateService:
    """
    خدمة تحديث المنتجات - تحتوي على جميع عمليات التحديث
    """
    
    # ============================================================
    # 📝 PRODUCT UPDATE MUTATIONS
    # ============================================================
    
    @staticmethod
    def update_product_info(qid: str, input_data: Dict[str, Any]) -> Optional[Dict]:
        """
        تحديث معلومات المنتج الأساسية
        
        Args:
            qid: معرف المنتج
            input_data: بيانات التحديث (name, description, status, etc.)
        
        Returns:
            Dict: بيانات المنتج المحدث
        """
        query = """
        mutation UpdateProductInfo($qid: String!, $input: UpdateProductInfoInput!) {
            updateProductInfo(qid: $qid, input: $input) {
                id
                qid
                name
                price
                status
                description
                updatedAt
            }
        }
        """
        return QomrahGraphQLClient.execute_query(query, {'qid': qid, 'input': input_data})
    
    @staticmethod
    def update_product_status(qid: str, status: str) -> Optional[Dict]:
        """
        تحديث حالة المنتج
        
        Args:
            qid: معرف المنتج
            status: الحالة الجديدة (ACTIVE, INACTIVE, DRAFT, etc.)
        """
        query = """
        mutation UpdateProductStatus($qid: String!, $status: String!) {
            updateProductStatus(qid: $qid, status: $status) {
                id
                qid
                status
                updatedAt
            }
        }
        """
        return QomrahGraphQLClient.execute_query(query, {'qid': qid, 'status': status})
    
    @staticmethod
    def update_product_pricing(qid: str, price: float, compare_at_price: Optional[float] = None) -> Optional[Dict]:
        """
        تحديث تسعير المنتج
        
        Args:
            qid: معرف المنتج
            price: السعر الجديد
            compare_at_price: السعر المقارن (اختياري)
        """
        query = """
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
        variables = {'qid': qid, 'price': price}
        if compare_at_price is not None:
            variables['compareAtPrice'] = compare_at_price
        return QomrahGraphQLClient.execute_query(query, variables)
    
    @staticmethod
    def update_product_dimensions(qid: str, dimensions: Dict[str, float]) -> Optional[Dict]:
        """
        تحديث أبعاد المنتج
        
        Args:
            qid: معرف المنتج
            dimensions: الأبعاد {length, width, height, unit?}
        """
        query = """
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
        return QomrahGraphQLClient.execute_query(query, {'qid': qid, 'dimensions': dimensions})
    
    @staticmethod
    def update_product_weight(qid: str, weight: float, unit: str = 'kg') -> Optional[Dict]:
        """
        تحديث وزن المنتج
        
        Args:
            qid: معرف المنتج
            weight: الوزن الجديد
            unit: وحدة الوزن (kg, g, lb, oz)
        """
        query = """
        mutation UpdateProductWeight($qid: String!, $weight: Float!, $unit: String!) {
            updateProductWeight(qid: $qid, weight: $weight, unit: $unit) {
                id
                qid
                weight
                unit
                updatedAt
            }
        }
        """
        return QomrahGraphQLClient.execute_query(query, {'qid': qid, 'weight': weight, 'unit': unit})
    
    @staticmethod
    def update_product_identification(qid: str, identification: Dict[str, Any]) -> Optional[Dict]:
        """
        تحديث بيانات تعريف المنتج (SKU, Barcode, etc.)
        
        Args:
            qid: معرف المنتج
            identification: بيانات التعريف {sku, barcode, barcodeType, hsCode, countryOfOrigin, mpn}
        """
        query = """
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
        return QomrahGraphQLClient.execute_query(query, {'qid': qid, 'identification': identification})
    
    @staticmethod
    def update_product_description(qid: str, description: str) -> Optional[Dict]:
        """
        تحديث وصف المنتج
        
        Args:
            qid: معرف المنتج
            description: النص الجديد للوصف
        """
        query = """
        mutation UpdateProductDescription($qid: String!, $description: String!) {
            updateProductDescription(qid: $qid, description: $description) {
                id
                qid
                description
                updatedAt
            }
        }
        """
        return QomrahGraphQLClient.execute_query(query, {'qid': qid, 'description': description})
    
    @staticmethod
    def update_product_seo(qid: str, seo_data: Dict[str, Any]) -> Optional[Dict]:
        """
        تحديث SEO للمنتج
        
        Args:
            qid: معرف المنتج
            seo_data: بيانات SEO {title, description, keywords, image, canonicalUrl}
        """
        query = """
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
        return QomrahGraphQLClient.execute_query(query, {'qid': qid, 'seo': seo_data})
    
    @staticmethod
    def update_product_collection(qid: str, collection_qids: List[str]) -> Optional[Dict]:
        """
        تحديث مجموعات المنتج
        
        Args:
            qid: معرف المنتج
            collection_qids: قائمة معرفات المجموعات
        """
        query = """
        mutation UpdateProductCollection($qid: String!, $collectionQids: [String!]!) {
            updateProductCollection(qid: $qid, collectionQids: $collectionQids) {
                id
                qid
                collections {
                    id
                    qid
                    name
                }
                updatedAt
            }
        }
        """
        return QomrahGraphQLClient.execute_query(query, {'qid': qid, 'collectionQids': collection_qids})
    
    @staticmethod
    def update_product_images(qid: str, images: List[str]) -> Optional[Dict]:
        """
        تحديث صور المنتج (استبدال كامل)
        
        Args:
            qid: معرف المنتج
            images: قائمة روابط الصور الجديدة
        """
        query = """
        mutation UpdateProductImages($qid: String!, $images: [String!]!) {
            updateProductImages(qid: $qid, images: $images) {
                id
                qid
                images
                updatedAt
            }
        }
        """
        return QomrahGraphQLClient.execute_query(query, {'qid': qid, 'images': images})
    
    @staticmethod
    def update_product_images_advanced(qid: str, new_images: List[str], removed_images: Optional[List[str]] = None) -> Optional[Dict]:
        """
        تحديث صور المنتج (إضافة وحذف)
        
        Args:
            qid: معرف المنتج
            new_images: قائمة الصور الجديدة للإضافة
            removed_images: قائمة الصور للحذف
        """
        query = """
        mutation UpdateProductImagesAdvanced($qid: String!, $newImages: [String!]!, $removedImages: [String!]) {
            updateProductImagesAdvanced(qid: $qid, newImages: $newImages, removedImages: $removedImages) {
                id
                qid
                images
                updatedAt
            }
        }
        """
        return QomrahGraphQLClient.execute_query(query, {'qid': qid, 'newImages': new_images, 'removedImages': removed_images or []})
    
    @staticmethod
    def check_product_slug(slug: str) -> Dict:
        """
        التحقق من توفر الـ Slug
        
        Args:
            slug: الاسم المختصر للتحقق
        
        Returns:
            Dict: {success: bool, message: str}
        """
        query = """
        query CheckProductSlug($slug: String!) {
            checkProductSlug(slug: $slug) {
                success
                message
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'slug': slug})
        return result.get('checkProductSlug', {}) if result else {}
    
    # ============================================================
    # 🗑️ DELETE OPERATIONS
    # ============================================================
    
    @staticmethod
    def delete_product(qid: str) -> bool:
        """
        حذف منتج
        
        Args:
            qid: معرف المنتج
        
        Returns:
            bool: نجاح العملية
        """
        query = """
        mutation DeleteProduct($qid: String!) {
            deleteProduct(qid: $qid)
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'qid': qid})
        return result.get('deleteProduct', False) if result else False
    
    @staticmethod
    def bulk_delete_products(qids: List[str]) -> bool:
        """
        حذف منتجات متعددة
        
        Args:
            qids: قائمة معرفات المنتجات
        
        Returns:
            bool: نجاح العملية
        """
        query = """
        mutation BulkDeleteProduct($qids: [String!]!) {
            bulkDeleteProduct(qids: $qids)
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'qids': qids})
        return result.get('bulkDeleteProduct', False) if result else False
    
    @staticmethod
    def bulk_update_products_status(qids: List[str], status: str) -> Optional[List[Dict]]:
        """
        تحديث حالة منتجات متعددة
        
        Args:
            qids: قائمة معرفات المنتجات
            status: الحالة الجديدة
        
        Returns:
            List[Dict]: قائمة المنتجات المحدثة
        """
        query = """
        mutation BulkUpdateProductsStatus($qids: [String!]!, $status: String!) {
            bulkUpdateProductsStatus(qids: $qids, status: $status) {
                id
                qid
                status
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'qids': qids, 'status': status})
        return result.get('bulkUpdateProductsStatus', []) if result else []
    
    # ============================================================
    # 🎨 VARIANT UPDATE MUTATIONS
    # ============================================================
    
    @staticmethod
    def update_variant_media(variant_qid: str, media: List[str]) -> Optional[Dict]:
        """
        تحديث وسائط الفاريانت
        
        Args:
            variant_qid: معرف الفاريانت
            media: قائمة روابط الوسائط
        """
        query = """
        mutation UpdateVariantMedia($variantQid: String!, $media: [String!]!) {
            updateVariantMedia(variantQid: $variantQid, media: $media) {
                id
                qid
                media
                updatedAt
            }
        }
        """
        return QomrahGraphQLClient.execute_query(query, {'variantQid': variant_qid, 'media': media})
    
    @staticmethod
    def update_variant_pricing(variant_qid: str, price: float, compare_at_price: Optional[float] = None) -> Optional[Dict]:
        """
        تحديث تسعير الفاريانت
        
        Args:
            variant_qid: معرف الفاريانت
            price: السعر الجديد
            compare_at_price: السعر المقارن (اختياري)
        """
        query = """
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
        variables = {'variantQid': variant_qid, 'price': price}
        if compare_at_price is not None:
            variables['compareAtPrice'] = compare_at_price
        return QomrahGraphQLClient.execute_query(query, variables)
    
    @staticmethod
    def remove_variant(variant_qid: str) -> bool:
        """
        حذف فاريانت
        
        Args:
            variant_qid: معرف الفاريانت
        
        Returns:
            bool: نجاح العملية
        """
        query = """
        mutation RemoveVariant($variantQid: String!) {
            removeVariantById(variantQid: $variantQid)
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'variantQid': variant_qid})
        return result.get('removeVariantById', False) if result else False
    
    @staticmethod
    def bulk_variant_update(variants: List[Dict]) -> Optional[List[Dict]]:
        """
        تحديث فاريانتات متعددة دفعة واحدة
        
        Args:
            variants: قائمة بيانات الفاريانتات {variantQid, price, media, etc.}
        """
        query = """
        mutation BulkVariantUpdate($variants: [VariantUpdateInput!]!) {
            bulkVariantUpdate(variants: $variants) {
                id
                qid
                name
                price
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'variants': variants})
        return result.get('bulkVariantUpdate', []) if result else []
    
    # ============================================================
    # 🎯 OPTION UPDATE MUTATIONS
    # ============================================================
    
    @staticmethod
    def create_option(input_data: Dict) -> Optional[Dict]:
        """
        إنشاء خيار جديد
        
        Args:
            input_data: بيانات الخيار {product, name, type, values}
        """
        query = """
        mutation CreateOption($input: CreateOptionInput!) {
            createOption(input: $input) {
                id
                qid
                name
                type
                values
                createdAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'input': input_data})
        return result.get('createOption') if result else None
    
    @staticmethod
    def update_option(option_qid: str, input_data: Dict) -> Optional[Dict]:
        """
        تحديث خيار
        
        Args:
            option_qid: معرف الخيار
            input_data: بيانات التحديث
        """
        query = """
        mutation UpdateOption($optionQid: String!, $input: UpdateOptionInput!) {
            updateOption(optionQid: $optionQid, input: $input) {
                id
                qid
                name
                values
                updatedAt
            }
        }
        """
        return QomrahGraphQLClient.execute_query(query, {'optionQid': option_qid, 'input': input_data})
    
    @staticmethod
    def remove_option(option_qid: str) -> bool:
        """
        حذف خيار
        
        Args:
            option_qid: معرف الخيار
        """
        query = """
        mutation RemoveOption($optionQid: String!) {
            removeOption(optionQid: $optionQid)
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'optionQid': option_qid})
        return result.get('removeOption', False) if result else False


# ============================================================
# 🚀 INSTANCE
# ============================================================

product_update = ProductUpdateService()
