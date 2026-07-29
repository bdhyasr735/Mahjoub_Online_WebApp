# apps/services/variant_service.py

from typing import Dict, Any, Optional, List
from .graphql_client import GraphQLClient


class VariantService:
    def __init__(self, client: GraphQLClient):
        self.client = client
    
    # =================================================================
    # 1. جلب المتغيرات (Variants) - التعديل بناءً على السجلات
    # =================================================================
    
    def get_by_product(self, product_qid: str) -> List[Dict]:
        """
        جلب جميع المتغيرات الخاصة بمنتج معين.
        """
        # ✅ التعديلات الحرفية بناءً على السجلات:
        # 1. السجلات طلبت تغيير $productQid إلى $productId (تم).
        # 2. السجلات رفضت الحقول المباشرة، لذا تم إضافة data { ... } (تم).
        # 3. السجلات رفضت _id، لذا تم استخدام id (تم).
        query = """
        query FindAllVariantsByProductId($productId: String!) {
            findAllVariantsByProductId(productId: $productId) {
                data {
                    id
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
        }
        """
        try:
            data = self.client.execute(query, {'productId': product_qid}, operation_name="FindAllVariantsByProductId")
            return data.get('findAllVariantsByProductId', {}).get('data', []) if data else []
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في جلب المتغيرات للمنتج {product_qid}: {e}")
            return []
    
    def get_by_qid(self, variant_qid: str) -> Optional[Dict]:
        query = """
        query FindVariantById($variantQid: String!) {
            findVariantById(variantQid: $variantQid) {
                data {
                    id
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
        }
        """
        try:
            data = self.client.execute(query, {'variantQid': variant_qid}, operation_name="FindVariantById")
            return data.get('findVariantById', {}).get('data') if data else None
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في جلب المتغير {variant_qid}: {e}")
            return None

    # =================================================================
    # 2. جلب الخيارات (Options) - التعديل بناءً على السجلات
    # =================================================================
    
    def get_all_options_for_product(self, qid: str) -> List[Dict[str, Any]]:
        # ✅ التعديل الحرفي بناءً على السجلات:
        # السجلات رفضت الحقول على المستوى الجذري، لذا تم إضافة data { ... }
        query = """
        query FindAllOptionsForProduct($qid: String!) {
            findAllOptionsForProduct(qid: $qid) {
                data {
                    qid
                    name
                    values {
                        option
                        label
                        sortOrder
                    }
                }
            }
        }
        """
        variables = {"qid": qid}
        try:
            result = self.client.execute(query, variables, operation_name="FindAllOptionsForProduct")
            return result.get('findAllOptionsForProduct', {}).get('data', []) if result else []
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في جلب خيارات المنتج {qid}: {e}")
            return []

    # =================================================================
    # 3. التحويرات (Mutations) - التعديل بناءً على السجلات
    # =================================================================
    
    def update_price(self, variant_qid: str, price: float) -> Optional[Dict]:
        query = """
        mutation UpdateVariantPricing($variantQid: String!, $price: Float!) {
            updateVariantPricing(variantQid: $variantQid, price: $price) {
                data {
                    id
                    qid
                    price
                    updatedAt
                }
            }
        }
        """
        try:
            data = self.client.execute(query, {'variantQid': variant_qid, 'price': price}, operation_name="UpdateVariantPricing")
            return data.get('updateVariantPricing', {}).get('data') if data else None
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في تحديث سعر المتغير {variant_qid}: {e}")
            return None
    
    def update_media(self, variant_qid: str, media: List[str]) -> Optional[Dict]:
        query = """
        mutation UpdateVariantMedia($variantQid: String!, $media: [String!]!) {
            updateVariantMedia(variantQid: $variantQid, media: $media) {
                data {
                    id
                    qid
                    media
                    updatedAt
                }
            }
        }
        """
        try:
            data = self.client.execute(query, {'variantQid': variant_qid, 'media': media}, operation_name="UpdateVariantMedia")
            return data.get('updateVariantMedia', {}).get('data') if data else None
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
                data {
                    id
                    qid
                    name
                    price
                    updatedAt
                }
            }
        }
        """
        try:
            data = self.client.execute(query, {'variants': variants}, operation_name="BulkVariantUpdate")
            return data.get('bulkVariantUpdate', {}).get('data', []) if data else []
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في التحديث الجماعي للمتغيرات: {e}")
            return []
