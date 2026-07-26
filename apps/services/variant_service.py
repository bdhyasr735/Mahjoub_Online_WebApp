# apps/services/variant_service.py

from typing import Dict, Any, Optional, List
from .graphql_client import GraphQLClient


class VariantService:
    def __init__(self, client: GraphQLClient):
        self.client = client
    
    # ========== الاستعلامات ==========
    
    def get_by_product(self, product_qid: str) -> List[Dict]:
        query = """
        query FindAllVariantsByProductId($productQid: String!) {
            findAllVariantsByProductId(productQid: $productQid) {
                id
                qid
                name
                price
                sku
                stock
                media
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
        query = """
        query FindVariantById($variantQid: String!) {
            findVariantById(variantQid: $variantQid) {
                id
                qid
                name
                price
                sku
                stock
                media
                createdAt
                updatedAt
            }
        }
        """
        try:
            data = self.client.execute(query, {'variantQid': variant_qid}, operation_name="FindVariantById")
            return data.get('findVariantById') if data else None
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في جلب المتغير {variant_qid}: {e}")
            return None
    
    # ========== التحويرات ==========
    
    def update_price(self, variant_qid: str, price: float) -> Optional[Dict]:
        query = """
        mutation UpdateVariantPricing($variantQid: String!, $price: Float!) {
            updateVariantPricing(variantQid: $variantQid, price: $price) {
                id
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
                id
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
                id
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
