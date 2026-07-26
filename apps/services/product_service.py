# coding: utf-8
# 📂 apps/services/product_service.py

"""
خدمة المنتجات - Product Service
"""

from typing import List, Optional, Dict, Any
from .graphql_client import GraphQLClient


class ProductService:
    """خدمة لإدارة المنتجات والبحث فيها عبر GraphQL"""
    
    def __init__(self, client: GraphQLClient):
        self.client = client
    
    # ========== الاستعلامات (Queries) ==========
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        جلب تفاصيل المنتج بواسطة المعرف (ID)
        """
        query = """
        query FindProductById($id: ID!) {
          findProductById(id: $id) {
            id
            qid
            name
            description
            price
            compareAtPrice
            costPerItem
            sku
            barcode
            quantity
            isActive
            isAvailable
            
            mainImage {
              id
              url
              altText
            }
            
            media {
              id
              url
              altText
            }
            
            categories {
              id
              name
            }
            
            variants {
              id
              sku
              price
              quantity
            }
            
            createdAt
            updatedAt
          }
        }
        """
        
        variables = {"id": product_id}
        result = self.client.execute(query, variables) or {}
        return result.get('findProductById')

    def get_product_by_qid(self, qid: str) -> Optional[Dict[str, Any]]:
        """
        جلب تفاصيل المنتج بواسطة QID
        """
        query = """
        query FindProductByQid($qid: String!) {
          findProductByQid(qid: $qid) {
            id
            qid
            name
            description
            price
            sku
            quantity
            isActive
            isAvailable
            mainImage {
              url
              altText
            }
          }
        }
        """
        
        variables = {"qid": qid}
        result = self.client.execute(query, variables) or {}
        return result.get('findProductByQid')

    def get_all_products(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        جلب قائمة المنتجات مع دعم التقسيم (Pagination)
        """
        query = """
        query FindAllProducts($limit: Int, $offset: Int) {
          findAllProducts(limit: $limit, offset: $offset) {
            id
            qid
            name
            price
            sku
            quantity
            isActive
            isAvailable
            mainImage {
              url
            }
          }
        }
        """
        
        variables = {"limit": limit, "offset": offset}
        result = self.client.execute(query, variables) or {}
        return result.get('findAllProducts', [])

    # ========== التحويرات (Mutations) ==========

    def update_product_price(self, product_id: str, price: float) -> Optional[Dict[str, Any]]:
        """
        تحديث سعر المنتج الأساسي
        """
        query = """
        mutation UpdateProductPrice($id: ID!, $price: Float!) {
          updateProductPrice(id: $id, price: $price) {
            id
            qid
            price
            updatedAt
          }
        }
        """
        
        variables = {"id": product_id, "price": price}
        result = self.client.execute(query, variables) or {}
        return result.get('updateProductPrice')

    def delete_product(self, product_id: str) -> bool:
        """
        حذف منتج بواسطة المعرف
        """
        query = """
        mutation RemoveProductById($id: ID!) {
          removeProductById(id: $id)
        }
        """
        
        variables = {"id": product_id}
        result = self.client.execute(query, variables) or {}
        return result.get('removeProductById', False)
