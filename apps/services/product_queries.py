# coding: utf-8
# 📂 apps/services/product_queries.py

from typing import Dict, List, Optional


class ProductQueries:
    """استعلامات المنتجات من قمرة"""

    def __init__(self, client):
        self.client = client

    def fetch_products(self, page: int = 1, limit: int = 50, **filters) -> Dict:
        """جلب قائمة المنتجات"""
        query = """
        query ($page: Int!, $limit: Int!, $title: String, $status: String) {
            findAllProducts(page: $page, limit: $limit, title: $title, status: $status) {
                id qid title slug description status quantity price compareAtPrice
                images { _id fileUrl }
                collections { qid title slug }
                variants { _id qid quantity price compareAtPrice }
                options { qid name values }
                seo { title description keywords }
                createdAt updatedAt
            }
        }
        """
        variables = {"page": page, "limit": limit}
        if filters.get('title'):
            variables["title"] = filters['title']
        if filters.get('status'):
            variables["status"] = filters['status']

        result = self.client.execute_query(query, variables)
        return {"data": result.get('findAllProducts', []), "pagination": {"page": page, "limit": limit}}

    def fetch_product_by_qid(self, qid: str) -> Optional[Dict]:
        """جلب منتج بواسطة QID"""
        query = """
        query ($qid: String!) {
            findProductByQid(qid: $qid) {
                id qid title slug description status quantity price compareAtPrice
                images { _id fileUrl }
                collections { qid title slug }
                variants { _id qid quantity price compareAtPrice }
                options { qid name values }
                seo { title description keywords }
                weight dimensions { length width height }
                identification { sku barcode barcodeType hsCode countryOfOrigin }
                createdAt updatedAt
            }
        }
        """
        result = self.client.execute_query(query, {"qid": qid})
        return result.get('findProductByQid') if result else None
