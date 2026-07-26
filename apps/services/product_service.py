# coding: utf-8
# 📂 apps/services/product_service.py

"""
خدمة المنتجات - Product Service (محدثة وشاملة للتوافق التام مع لوحة التحكم)
"""

from typing import List, Optional, Dict, Any
from .graphql_client import GraphQLClient


class ProductService:
    """خدمة لإدارة المنتجات والبحث فيها عبر GraphQL"""
    
    def __init__(self, client: GraphQLClient):
        self.client = client
    
    # ============================================================
    # 📌 الاستعلامات (Queries)
    # ============================================================
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """جلب تفاصيل المنتج بواسطة المعرف (ID)"""
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
            status
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
        """جلب تفاصيل المنتج بواسطة QID"""
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
            status
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

    # ✅ دالة متوافقة مع الاستدعاء في routes.py
    def get_by_qid(self, qid: str) -> Optional[Dict[str, Any]]:
        return self.get_product_by_qid(qid)

    def get_all_products(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """جلب قائمة المنتجات مع دعم التقسيم (Pagination)"""
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
            status
            mainImage {
              url
            }
          }
        }
        """
        variables = {"limit": limit, "offset": offset}
        result = self.client.execute(query, variables) or {}
        return result.get('findAllProducts', [])

    # ✅ دالة متوافقة مع الاستدعاء `products_service.get_all()` في routes.py
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self.get_all_products(limit=limit, offset=offset)

    # ============================================================
    # 📌 التعديلات والتحويرات (Mutations)
    # ============================================================

    def create(self, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """إنشاء منتج جديد في قمرة"""
        query = """
        mutation CreateProduct($input: ProductInput!) {
          createProduct(input: $input) {
            id
            qid
            name
            price
            status
          }
        }
        """
        variables = {"input": product_data}
        result = self.client.execute(query, variables) or {}
        return result.get('createProduct')

    def update(self, qid: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """تحديث بيانات منتج موجود بواسطة QID"""
        query = """
        mutation UpdateProduct($qid: String!, $input: ProductUpdateInput!) {
          updateProduct(qid: $qid, input: $input) {
            id
            qid
            name
            price
            status
          }
        }
        """
        variables = {"qid": qid, "input": update_data}
        result = self.client.execute(query, variables) or {}
        return result.get('updateProduct')

    def update_status(self, qid: str, status: str) -> Optional[Dict[str, Any]]:
        """تحديث حالة المنتج (PUBLISHED, REJECTED, DRAFT, ARCHIVED)"""
        query = """
        mutation UpdateProductStatus($qid: String!, $status: String!) {
          updateProductStatus(qid: $qid, status: $status) {
            id
            qid
            status
          }
        }
        """
        variables = {"qid": qid, "status": status}
        result = self.client.execute(query, variables) or {}
        return result.get('updateProductStatus')

    def update_product_price(self, product_id: str, price: float) -> Optional[Dict[str, Any]]:
        """تحديث سعر المنتج الأساسي"""
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
        """حذف منتج بواسطة المعرف (ID)"""
        query = """
        mutation RemoveProductById($id: ID!) {
          removeProductById(id: $id)
        }
        """
        variables = {"id": product_id}
        result = self.client.execute(query, variables) or {}
        return result.get('removeProductById', False)

    def delete(self, qid_or_id: str) -> bool:
        """حذف منتج (دالة موحدة تدعم الحذف بـ QID أو ID المتوافقة مع routes.py)"""
        query = """
        mutation RemoveProductByQid($qid: String!) {
          removeProductByQid(qid: $qid)
        }
        """
        variables = {"qid": qid_or_id}
        result = self.client.execute(query, variables) or {}
        res = result.get('removeProductByQid')
        
        if res is None:
            return self.delete_product(qid_or_id)
        return bool(res)
