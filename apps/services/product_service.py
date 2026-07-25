"""
خدمة المتغيرات - Variant Service
"""

from typing import List, Optional, Dict
from graphql_client import GraphQLClient


class VariantService:
    """خدمة لإدارة متغيرات المنتجات"""
    
    def __init__(self, client: GraphQLClient, queries_path: str = 'apps/services/variant_queries.graphql'):
        self.client = client
        
        try:
            with open(queries_path, 'r', encoding='utf-8') as f:
                self.queries = f.read()
        except FileNotFoundError:
            self.queries = ""
    
    def get_variants_by_product(self, product_id: str) -> List[Dict]:
        """
        جلب جميع متغيرات المنتج
        """
        query = """
        query FindAllVariantsByProductId($productId: ID!) {
          findAllVariantsByProductId(productId: $productId) {
            id
            qid
            sku
            barcode
            price
            compareAtPrice
            costPerItem
            quantity
            weight
            weightUnit
            position
            isActive
            isAvailable
            isDefault
            
            options {
              id
              name
              value
              position
            }
            
            image {
              id
              url
              altText
              width
              height
            }
            
            inventory {
              id
              quantity
              available
              reserved
              location
              warehouse
            }
            
            product {
              id
              qid
              name
              price
              mainImage {
                url
                altText
              }
            }
          }
        }
        """
        
        variables = {"productId": product_id}
        result = self.client.execute(query, variables)
        return result.get('findAllVariantsByProductId', [])
    
    def get_variant_by_id(self, variant_id: str) -> Optional[Dict]:
        """
        جلب متغير بواسطة ID
        """
        query = """
        query FindVariantById($id: ID!) {
          findVariantById(id: $id) {
            id
            qid
            sku
            barcode
            price
            compareAtPrice
            costPerItem
            quantity
            weight
            weightUnit
            position
            isActive
            isAvailable
            isDefault
            
            options {
              id
              name
              value
              position
            }
            
            image {
              id
              url
              altText
              width
              height
            }
            
            inventory {
              id
              quantity
              available
              reserved
              location
              warehouse
            }
            
            product {
              id
              qid
              name
              price
              mainImage {
                url
                altText
              }
            }
          }
        }
        """
        
        variables = {"id": variant_id}
        result = self.client.execute(query, variables)
        return result.get('findVariantById')
    
    def get_variant_by_sku(self, sku: str) -> Optional[Dict]:
        """
        جلب متغير بواسطة SKU
        """
        query = """
        query FindVariantBySku($sku: String!) {
          findVariantBySku(sku: $sku) {
            id
            qid
            sku
            barcode
            price
            compareAtPrice
            quantity
            isAvailable
            options {
              name
              value
            }
            image {
              url
              altText
            }
            inventory {
              quantity
              available
              location
            }
            product {
              id
              name
              price
            }
          }
        }
        """
        
        variables = {"sku": sku}
        result = self.client.execute(query, variables)
        return result.get('findVariantBySku')
    
    def get_variants_inventory(self, product_id: str) -> List[Dict]:
        """
        جلب مخزون متغيرات المنتج
        """
        query = """
        query GetVariantsInventory($productId: ID!) {
          findAllVariantsByProductId(productId: $productId) {
            id
            sku
            quantity
            isAvailable
            inventory {
              id
              quantity
              available
              reserved
              location
            }
            options {
              name
              value
            }
          }
        }
        """
        
        variables = {"productId": product_id}
        result = self.client.execute(query, variables)
        return result.get('findAllVariantsByProductId', [])
    
    def get_variants_prices(self, product_id: str) -> List[Dict]:
        """
        جلب أسعار متغيرات المنتج
        """
        query = """
        query GetVariantsPrices($productId: ID!) {
          findAllVariantsByProductId(productId: $productId) {
            id
            sku
            price
            compareAtPrice
            costPerItem
            currency
            options {
              name
              value
            }
          }
        }
        """
        
        variables = {"productId": product_id}
        result = self.client.execute(query, variables)
        return result.get('findAllVariantsByProductId', [])
    
    def get_variant_by_options(self, product_id: str, options: Dict[str, str]) -> Optional[Dict]:
        """
        جلب متغير حسب الخيارات (مثل: اللون والحجم)
        """
        variants = self.get_variants_by_product(product_id)
        
        for variant in variants:
            variant_options = {opt['name']: opt['value'] for opt in variant.get('options', [])}
            if all(variant_options.get(k) == v for k, v in options.items()):
                return variant
        
        return None
    
    def get_available_variants(self, product_id: str) -> List[Dict]:
        """
        جلب المتغيرات المتاحة للبيع فقط
        """
        variants = self.get_variants_by_product(product_id)
        return [v for v in variants if v.get('isAvailable') and v.get('quantity', 0) > 0]
