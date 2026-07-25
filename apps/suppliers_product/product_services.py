
"""
خدمة المنتجات - Product Service
"""

from typing import List, Optional, Dict
from core.graphql_client import GraphQLClient

class ProductService:
    def __init__(self, client: GraphQLClient):
        self.client = client
        with open('apps/services/product_queries.graphql', 'r', encoding='utf-8') as f:
            self.queries = f.read()

    def get_product_by_qid(self, qid: str) -> Optional[Dict]:
        query = """
        query FindProductByQid($qid: String!) {
            findProductByQid(qid: $qid) {
                id
                qid
                name
                description
                price
                compareAtPrice
                status
                isActive
            }
        }
        """
        result = self.client.execute(query, {"qid": qid})
        return result.get('findProductByQid') if result else None
