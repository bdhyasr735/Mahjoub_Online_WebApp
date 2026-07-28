# coding: utf-8
# apps/services/collection_service.py

"""
خدمة المجموعات - Collection Service
"""

from typing import List, Optional, Dict
from .graphql_client import GraphQLClient


class CollectionService:
    """خدمة لإدارة المجموعات"""
    
    def __init__(self, client: GraphQLClient, queries_path: str = 'apps/services/collection_queries.graphql'):
        self.client = client
        
        try:
            with open(queries_path, 'r', encoding='utf-8') as f:
                self.queries = f.read()
        except FileNotFoundError:
            print(f"⚠️ [CollectionService]: لم يتم العثور على ملف الاستعلامات: {queries_path}")
            self.queries = ""
    
    def get_all_collections(self) -> List[Dict]:
        """
        جلب جميع المجموعات
        
        Returns:
            قائمة المجموعات
        """
        query = """
        query FindAllCollections {
            findAllCollections {
                id
                qid
                title
                description
                handle
                image {
                    id
                    url
                    altText
                    width
                    height
                }
                productsCount
                isActive
                isFeatured
                createdAt
                updatedAt
                products {
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
        
        try:
            result = self.client.execute(query, operation_name="FindAllCollections")
            return result.get('findAllCollections', []) if result else []
        except Exception as e:
            print(f"❌ [CollectionService]: خطأ في جلب المجموعات: {e}")
            return []
    
    def get_collection_by_qid(self, qid: str) -> Optional[Dict]:
        """
        جلب مجموعة بواسطة QID أو المعرف
        
        Args:
            qid: المعرف الفريد للمجموعة
            
        Returns:
            بيانات المجموعة
        """
        query = """
        query FindCollectionByQid($id: ID!) {
            findCollectionByQid(id: $id) {
                id
                qid
                title
                description
                handle
                image {
                    id
                    url
                    altText
                    width
                    height
                }
                productsCount
                isActive
                isFeatured
                createdAt
                updatedAt
                products {
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
                }
            }
        }
        """
        
        variables = {"id": qid}
        
        try:
            result = self.client.execute(query, variables, operation_name="FindCollectionByQid")
            return result.get('findCollectionByQid') if result else None
        except Exception as e:
            print(f"❌ [CollectionService]: خطأ في جلب المجموعة {qid}: {e}")
            return None
    
    def get_products_by_collection(self, collection_qid: str) -> List[Dict]:
        """
        جلب منتجات مجموعة معينة
        
        Args:
            collection_qid: المعرف الفريد للمجموعة
            
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
                currency
                sku
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
                    width
                    height
                    position
                }
                variants {
                    id
                    sku
                    price
                    compareAtPrice
                    quantity
                    isAvailable
                    image {
                        url
                        altText
                    }
                    inventory {
                        quantity
                        available
                    }
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
                }
            }
        }
        """
        
        variables = {"id": collection_qid}
        
        try:
            result = self.client.execute(query, variables, operation_name="FindAllProductsForCollection")
            return result.get('findAllProductsForCollection', []) if result else []
        except Exception as e:
            print(f"❌ [CollectionService]: خطأ في جلب منتجات المجموعة {collection_qid}: {e}")
            return []
