"""
خدمة المنتجات - Product Service
"""

from typing import List, Optional, Dict, Any
from graphql_client import GraphQLClient


class ProductService:
    """خدمة لإدارة المنتجات"""
    
    def __init__(self, client: GraphQLClient):
        self.client = client
        
        # تحميل استعلامات المنتج
        with open('product_queries.graphql', 'r') as f:
            self.queries = f.read()
    
    def get_all_products(self, input_data: Optional[Dict] = None) -> List[Dict]:
        """
        جلب جميع المنتجات
        
        Args:
            input_data: مدخلات البحث والترشيح
            
        Returns:
            قائمة المنتجات
        """
        query = """
        query FindAllProducts($input: GetAllProductsInput) {
          findAllProducts(input: $input) {
            id
            qid
            name
            description
            price
            compareAtPrice
            quantity
            sku
            status
            isActive
            isAvailable
            mainImage {
              url
              altText
            }
            variants {
              id
              sku
              price
              quantity
              options {
                name
                value
              }
            }
            inventory {
              quantity
              available
              reserved
            }
            collections {
              id
              name
            }
          }
        }
        """
        
        variables = {"input": input_data or {}}
        result = self.client.execute(query, variables)
        return result.get('findAllProducts', [])
    
    def get_product_by_qid(self, qid: str) -> Optional[Dict]:
        """
        جلب منتج بواسطة QID
        
        Args:
            qid: المعرف الفريد للمنتج
            
        Returns:
            بيانات المنتج
        """
        query = """
        query FindProductByQid($qid: String!) {
          findProductByQid(qid: $qid) {
            id
            qid
            name
            description
            price
            compareAtPrice
            costPerItem
            currency
            sku
            barcode
            quantity
            status
            isActive
            isAvailable
            mainImage {
              id
              url
              altText
              width
              height
            }
            images {
              id
              url
              altText
              position
            }
            options {
              id
              name
              values {
                id
                value
                hexCode
                image {
                  url
                }
              }
            }
            variants {
              id
              sku
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
                reserved
                location
              }
            }
            collections {
              id
              name
              handle
            }
            category {
              id
              name
              handle
            }
            brand {
              id
              name
              logo {
                url
              }
            }
            ratings {
              average
              count
            }
            inventory {
              quantity
              available
              reserved
              location
              warehouse
            }
            seo {
              title
              description
            }
            translations {
              locale
              name
              description
            }
            metafields {
              namespace
              key
              value
            }
          }
        }
        """
        
        variables = {"qid": qid}
        result = self.client.execute(query, variables)
        return result.get('findProductByQid')
    
    def get_product_variants(self, product_id: str) -> List[Dict]:
        """
        جلب جميع متغيرات المنتج
        
        Args:
            product_id: معرف المنتج
            
        Returns:
            قائمة المتغيرات
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
            options {
              id
              name
              value
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
            }
          }
        }
        """
        
        variables = {"productId": product_id}
        result = self.client.execute(query, variables)
        return result.get('findAllVariantsByProductId', [])
    
    def get_product_inventory(self, product_id: str) -> Dict:
        """
        جلب مخزون المنتج
        
        Args:
            product_id: معرف المنتج
            
        Returns:
            بيانات المخزون
        """
        query = """
        query GetProductInventory($productId: ID!) {
          findProductByQid(qid: $productId) {
            id
            qid
            name
            quantity
            inventory {
              id
              quantity
              available
              reserved
              location
              warehouse
            }
            variants {
              id
              sku
              quantity
              isAvailable
              options {
                name
                value
              }
              inventory {
                quantity
                available
                reserved
                location
              }
            }
          }
        }
        """
        
        variables = {"productId": product_id}
        result = self.client.execute(query, variables)
        return result.get('findProductByQid', {})
    
    def get_product_colors_and_prices(self, qid: str) -> Dict:
        """
        جلب ألوان وأسعار المنتج
        
        Args:
            qid: المعرف الفريد للمنتج
            
        Returns:
            بيانات الألوان والأسعار
        """
        query = """
        query GetProductColorsAndPrices($qid: String!) {
          findProductByQid(qid: $qid) {
            id
            qid
            name
            price
            compareAtPrice
            currency
            options {
              id
              name
              values {
                id
                value
                hexCode
                image {
                  url
                  altText
                }
              }
            }
            variants {
              id
              sku
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
              }
            }
          }
        }
        """
        
        variables = {"qid": qid}
        result = self.client.execute(query, variables)
        return result.get('findProductByQid', {})
    
    def get_top_viewed_products(self) -> List[Dict]:
        """
        جلب المنتجات الأكثر مشاهدة
        
        Returns:
            قائمة المنتجات الأكثر مشاهدة
        """
        query = """
        query FindTopViewedProducts {
          FindTopViewedProducts {
            id
            qid
            name
            price
            compareAtPrice
            views
            mainImage {
              url
              altText
            }
            ratings {
              average
              count
            }
          }
        }
        """
        
        result = self.client.execute(query, {})
        return result.get('FindTopViewedProducts', [])
    
    def get_product_status(self) -> List[Dict]:
        """
        جلب حالة المنتجات
        
        Returns:
            قائمة حالات المنتجات
        """
        query = """
        query FindProductStatus {
          findProductStatus {
            id
            qid
            name
            status
            isActive
            isAvailable
            isPublished
            isDraft
            isArchived
            createdAt
            updatedAt
          }
        }
        """
        
        result = self.client.execute(query, {})
        return result.get('findProductStatus', [])
    
    def search_products(self, search_term: str, limit: int = 20) -> List[Dict]:
        """
        البحث عن المنتجات
        
        Args:
            search_term: مصطلح البحث
            limit: عدد النتائج
            
        Returns:
            قائمة المنتجات
        """
        return self.get_all_products({
            "search": search_term,
            "limit": limit,
            "isActive": True
        })
    
    def get_products_by_collection(self, collection_id: str) -> List[Dict]:
        """
        جلب منتجات مجموعة معينة
        
        Args:
            collection_id: معرف المجموعة
            
        Returns:
            قائمة المنتجات
        """
        query = """
        query FindAllProductsForCollection($id: ID!) {
          findAllProductsForCollection(id: $id) {
            id
            qid
            name
            description
            price
            compareAtPrice
            mainImage {
              url
              altText
            }
            variants {
              id
              price
              sku
              quantity
            }
            inventory {
              quantity
              available
            }
          }
        }
        """
        
        variables = {"id": collection_id}
        result = self.client.execute(query, variables)
        return result.get('findAllProductsForCollection', [])
    
    def get_products_by_price_range(self, min_price: float, max_price: float) -> List[Dict]:
        """
        جلب منتجات حسب نطاق السعر
        
        Args:
            min_price: أقل سعر
            max_price: أعلى سعر
            
        Returns:
            قائمة المنتجات
        """
        return self.get_all_products({
            "minPrice": min_price,
            "maxPrice": max_price,
            "isActive": True
        })
