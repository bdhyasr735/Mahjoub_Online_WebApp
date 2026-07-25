# apps/services/collection_service.py

from typing import Dict, Any, Optional, List
from .graphql_client import GraphQLClient


class CollectionService:
    def __init__(self, client: GraphQLClient):
        self.client = client
    
    # ========== الاستعلامات ==========
    
    def get_all(self) -> List[Dict]:
        query = """
        query {
            findAllCollections {
                id qid name description image productsCount
                createdAt updatedAt
            }
        }
        """
        return self.client.execute(query).get('findAllCollections', [])
    
    def get_by_qid(self, qid: str) -> Optional[Dict]:
        query = """
        query($qid: String!) {
            findCollectionByQid(qid: $qid) {
                id qid name description image
                products { id qid name price }
                createdAt updatedAt
            }
        }
        """
        return self.client.execute(query, {'qid': qid}).get('findCollectionByQid')
    
    def get_products(self, collection_qid: str) -> List[Dict]:
        query = """
        query($collectionQid: String!) {
            findAllProductsForCollection(collectionQid: $collectionQid) {
                id qid name price status
            }
        }
        """
        return self.client.execute(query, {'collectionQid': collection_qid}).get('findAllProductsForCollection', [])
    
    # ========== التحويرات ==========
    
    def create(self, input_data: Dict) -> Optional[Dict]:
        query = """
        mutation($input: CreateCollectionInput!) {
            createCollection(input: $input) {
                id qid name description createdAt
            }
        }
        """
        return self.client.execute(query, {'input': input_data}).get('createCollection')
    
    def update(self, qid: str, input_data: Dict) -> Optional[Dict]:
        query = """
        mutation($qid: String!, $input: UpdateCollectionInput!) {
            updateCollection(qid: $qid, input: $input) {
                id qid name description updatedAt
            }
        }
        """
        return self.client.execute(query, {'qid': qid, 'input': input_data}).get('updateCollection')
    
    def delete(self, qid: str) -> bool:
        query = "mutation($qid: String!) { removeCollection(qid: $qid) }"
        result = self.client.execute(query, {'qid': qid})
        return result.get('removeCollection', False) if result else False
    
    def add_product(self, product_qid: str, collection_qids: List[str]) -> Optional[Dict]:
        query = """
        mutation($productQid: String!, $collectionQids: [String!]!) {
            AddProductToCollections(productQid: $productQid, collectionQids: $collectionQids) {
                id qid collections { id name }
            }
        }
        """
        return self.client.execute(query, {'productQid': product_qid, 'collectionQids': collection_qids}).get('AddProductToCollections')
