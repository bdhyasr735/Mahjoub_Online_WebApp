# apps/services/variant_service.py

from typing import Dict, Any, Optional, List
from .graphql_client import GraphQLClient


class VariantService:
    def __init__(self, client: GraphQLClient):
        self.client = client
    
    # =================================================================
    # 1. جلب المتغيرات (Variants) - تم تعديلها لتتوافق مع الساندبوكس
    # =================================================================
    
    def get_by_product(self, product_qid: str) -> List[Dict]:
        """
        جلب جميع المتغيرات الخاصة بمنتج معين.
        """
        query = """
        query FindAllVariantsByProductId($productQid: String!) {
            findAllVariantsByProductId(productQid: $productQid) {
                _id
                qid
                quantity
                pricing {
                    price
                    compareAtPrice
                    originalPrice
                }
                options {
                    label
                }
            }
        }
        """
        try:
            data = self.client.execute(query, {'productQid': product_qid}, operation_name="FindAllVariantsByProductId")
            return data.get('findAllVariantsByProductId', []) if data else []
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في جلب المتغيرات للمنتج {product_qid}: {e}")
            return []
    
    def get_by_qid(self, variant_qid: str) -> Optional[Dict]:
        """
        جلب متغير محدد بواسطة الـ QID الخاص به.
        """
        query = """
        query FindVariantById($variantQid: String!) {
            findVariantById(variantQid: $variantQid) {
                _id
                qid
                quantity
                pricing {
                    price
                    compareAtPrice
                    originalPrice
                }
                options {
                    label
                }
            }
        }
        """
        try:
            data = self.client.execute(query, {'variantQid': variant_qid}, operation_name="FindVariantById")
            return data.get('findVariantById') if data else None
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في جلب المتغير {variant_qid}: {e}")
            return None

    # =================================================================
    # 2. جلب الخيارات (Options) - تم تعديلها لتتوافق مع الساندبوكس
    # =================================================================
    
    def get_all_options_for_product(self, qid: str) -> List[Dict[str, Any]]:
        """
        جلب جميع خيارات المنتج (مثل: اللون، المقاس) بناءً على QID المنتج.
        """
        # ✅ استعلام ناجح في الساندبوكس (يستخدم option, label, sortOrder)
        query = """
        query FindAllOptionsForProduct($qid: String!) {
            findAllOptionsForProduct(qid: $qid) {
                qid
                name
                values {
                    option
                    label
                    sortOrder
                }
            }
        }
        """
        variables = {"qid": qid}
        try:
            result = self.client.execute(query, variables, operation_name="FindAllOptionsForProduct")
            return result.get('findAllOptionsForProduct', []) if result else []
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في جلب خيارات المنتج {qid}: {e}")
            return []

    # =================================================================
    # 3. ملاحظة هامة (تم حذف الدالة الخاطئة)
    # =================================================================
    # ❌ تم حذف دالة get_product_with_options_and_variants نهائياً
    # لأن الساندبوكس أكد أن استعلام "product(qid)" غير مدعوم في السيرفر
    # واستخدامه يسبب خطأ 500. بدلاً من ذلك، نستخدم get_by_product
    # و get_all_options_for_product بشكل منفصل في ملف crud.py.

    # =================================================================
    # 4. التحويرات (Mutations) - تحديث وحذف المتغيرات
    # =================================================================
    
    def update_price(self, variant_qid: str, price: float) -> Optional[Dict]:
        query = """
        mutation UpdateVariantPricing($variantQid: String!, $price: Float!) {
            updateVariantPricing(variantQid: $variantQid, price: $price) {
                _id
                qid
                price
                updatedAt
            }
        }
        """
        try:
            data = self.client.execute(query, {'variantQid': variant_qid, 'price': price}, operation_name="UpdateVariantPricing")
            return data.get('updateVariantPricing') if data else None
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في تحديث سعر المتغير {variant_qid}: {e}")
            return None
    
    def update_media(self, variant_qid: str, media: List[str]) -> Optional[Dict]:
        query = """
        mutation UpdateVariantMedia($variantQid: String!, $media: [String!]!) {
            updateVariantMedia(variantQid: $variantQid, media: $media) {
                _id
                qid
                media
                updatedAt
            }
        }
        """
        try:
            data = self.client.execute(query, {'variantQid': variant_qid, 'media': media}, operation_name="UpdateVariantMedia")
            return data.get('updateVariantMedia') if data else None
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في تحديث وسائط المتغير {variant_qid}: {e}")
            return None
    
    def delete(self, variant_qid: str) -> bool:
        query = """
        mutation RemoveVariantById($variantQid: String!) {
            removeVariantById(variantQid: $variantQid)
        }
        """
        try:
            data = self.client.execute(query, {'variantQid': variant_qid}, operation_name="RemoveVariantById")
            return data.get('removeVariantById', False) if data else False
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في حذف المتغير {variant_qid}: {e}")
            return False
    
    def bulk_update(self, variants: List[Dict]) -> List[Dict]:
        query = """
        mutation BulkVariantUpdate($variants: [VariantUpdateInput!]!) {
            bulkVariantUpdate(variants: $variants) {
                _id
                qid
                name
                price
                updatedAt
            }
        }
        """
        try:
            data = self.client.execute(query, {'variants': variants}, operation_name="BulkVariantUpdate")
            return data.get('bulkVariantUpdate', []) if data else []
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في التحديث الجماعي للمتغيرات: {e}")
            return []
