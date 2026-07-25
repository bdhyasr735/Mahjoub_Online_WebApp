# coding: utf-8
# 📂 apps/suppliers_product/product_services.py

"""
خدمة المنتجات - Product Service
"""

from typing import List, Optional, Dict
from apps.services.graphql_client import GraphQLClient

class ProductService:
    def __init__(self, client: GraphQLClient):
        self.client = client
        try:
            with open('apps/services/product_queries.graphql', 'r', encoding='utf-8') as f:
                self.queries = f.read()
        except FileNotFoundError:
            self.queries = ""

    def get_product_by_qid(self, qid: str) -> Optional[Dict]:
        query = """
        query FindProductByQid($qid: String!) {
            findProductByQid(qid: $qid) {
                id
                qid
                title
                name
                sku
                description
                price
                compareAtPrice
                status
                isActive
                quantity
                images {
                    url
                }
            }
        }
        """
        result = self.client.execute(query, {"qid": qid})
        return result.get('findProductByQid') if result else None
