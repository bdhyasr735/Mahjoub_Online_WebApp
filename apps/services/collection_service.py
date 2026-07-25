"""
خدمة المجموعات - Collection Service
"""

from typing import List, Optional, Dict
from graphql_client import GraphQLClient


class CollectionService:
    """خدمة لإدارة المجموعات"""
    
    def __init__(self, client: GraphQLClient):
        self.client = client
        
        with open('collection_queries.graphql', 'r') as f:
            self.queries = f.read()
    
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
            name
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
        
        result = self.client.execute(query, {})
        return result.get('findAllCollections', [])
    
    def get_collection_by_qid(self, qid: str) -> Optional[Dict]:
        """
        جلب مجموعة بواسطة QID
        
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
            name
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
        result = self.client.execute(query, variables)
        return result.get
