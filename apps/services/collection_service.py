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
                success
                message
                data {
                    qid
                    title
                    image {
                        fileUrl
                    }
                }
            }
        }
        """
        
        try:
            print(f"🔍 [CollectionService] جلب جميع المجموعات...")
            result = self.client.execute(query, operation_name="FindAllCollections")
            print(f"🔍 [CollectionService] Result: {result}")
            
            if result and "findAllCollections" in result:
                collections_data = result.get('findAllCollections', {})
                collections = collections_data.get('data', [])
                print(f"✅ [CollectionService] تم جلب {len(collections)} مجموعة")
                return collections
            return []
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
                success
                message
                data {
                    qid
                    title
                    description
                    handle
                    image {
                        id
                        fileUrl
                        width
                        height
                    }
                    productsCount
                    isActive
                    isFeatured
                    createdAt
                    updatedAt
                }
            }
        }
        """
        
        variables = {"id": qid}
        
        try:
            print(f"🔍 [CollectionService] جلب المجموعة بـ QID: {qid}")
            result = self.client.execute(query, variables, operation_name="FindCollectionByQid")
            print(f"🔍 [CollectionService] Result: {result}")
            
            if result and "findCollectionByQid" in result:
                collection_data = result.get('findCollectionByQid', {})
                return collection_data.get('data') if collection_data.get('success') else None
            return None
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
                success
                message
                data {
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
                        fileUrl
                        width
                        height
                    }
                    images {
                        id
                        fileUrl
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
                            fileUrl
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
                            fileUrl
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
        }
        """
        
        variables = {"id": collection_qid}
        
        try:
            print(f"🔍 [CollectionService] جلب منتجات المجموعة: {collection_qid}")
            result = self.client.execute(query, variables, operation_name="FindAllProductsForCollection")
            print(f"🔍 [CollectionService] Result: {result}")
            
            if result and "findAllProductsForCollection" in result:
                products_data = result.get('findAllProductsForCollection', {})
                return products_data.get('data', []) if products_data.get('success') else []
            return []
        except Exception as e:
            print(f"❌ [CollectionService]: خطأ في جلب منتجات المجموعة {collection_qid}: {e}")
            return []
