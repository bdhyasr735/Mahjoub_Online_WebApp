# apps/services/variant_service.py

from typing import Dict, Any, Optional, List
from .graphql_client import GraphQLClient


class VariantService:
    def __init__(self, client: GraphQLClient):
        self.client = client
    
    # ========== الاستعلامات ==========
    
    def get_by_product(self, product_qid: str) -> List[Dict]:
        query = """
        query($productQid: String!) {
            findAllVariantsByProductId(productQid: $productQid) {
                id qid name price sku stock media
            }
        }
        """
        return self.client.execute(query, {'productQid': product_qid}).get('findAllVariantsByProductId', [])
    
    def get_by_qid(self, variant_qid: str) -> Optional[Dict]:
        query = """
        query($variantQid: String!) {
            findVariantById(variantQid: $variantQid) {
                id qid name price sku stock media
                createdAt updatedAt
            }
        }
        """
        return self.client.execute(query, {'variantQid': variant_qid}).get('findVariantById')
    
    # ========== التحويرات ==========
    
    def update_price(self, variant_qid: str, price: float) -> Optional[Dict]:
        query = """
        mutation($variantQid: String!, $price: Float!) {
            updateVariantPricing(variantQid: $variantQid, price: $price) {
                id qid price updatedAt
            }
        }
        """
        return self.client.execute(query, {'variantQid': variant_qid, 'price': price}).get('updateVariantPricing')
    
    def update_media(self, variant_qid: str, media: List[str]) -> Optional[Dict]:
        query = """
        mutation($variantQid: String!, $media: [String!]!) {
            updateVariantMedia(variantQid: $variantQid, media: $media) {
                id qid media updatedAt
            }
        }
        """
        return self.client.execute(query, {'variantQid': variant_qid, 'media': media}).get('updateVariantMedia')
    
    def delete(self, variant_qid: str) -> bool:
        query = "mutation($variantQid: String!) { removeVariantById(variantQid: $variantQid) }"
        result = self.client.execute(query, {'variantQid': variant_qid})
        return result.get('removeVariantById', False) if result else False
    
    def bulk_update(self, variants: List[Dict]) -> List[Dict]:
        query = """
        mutation($variants: [VariantUpdateInput!]!) {
            bulkVariantUpdate(variants: $variants) {
                id qid name price updatedAt
            }
        }
        """
        return self.client.execute(query, {'variants': variants}).get('bulkVariantUpdate', [])
