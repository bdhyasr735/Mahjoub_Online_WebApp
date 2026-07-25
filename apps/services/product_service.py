# apps/services/product_service.py

from typing import Dict, Any, Optional, List
from .graphql_client import GraphQLClient


class ProductService:
    def __init__(self, client: GraphQLClient):
        self.client = client
    
    # ========== الاستعلامات ==========
    
    def get_all(self) -> List[Dict]:
        query = """
        query {
            findAllProducts {
                id qid name price status description images
                createdAt updatedAt
            }
        }
        """
        return self.client.execute(query).get('findAllProducts', [])
    
    def get_by_qid(self, qid: str) -> Optional[Dict]:
        query = """
        query($qid: String!) {
            findProductByQid(qid: $qid) {
                id qid name price status description
                images weight
                dimensions { length width height }
                seo { title description keywords }
                collections { id name }
                variants { id qid name price sku }
                options { id name values }
                createdAt updatedAt
            }
        }
        """
        return self.client.execute(query, {'qid': qid}).get('findProductByQid')
    
    def get_status(self, qid: str) -> Optional[Dict]:
        query = """
        query($qid: String!) {
            findProductStatus(qid: $qid) {
                id status publishedAt
            }
        }
        """
        return self.client.execute(query, {'qid': qid}).get('findProductStatus')
    
    def get_top_viewed(self, limit: int = 10) -> List[Dict]:
        query = """
        query($limit: Int!) {
            FindTopViewedProducts(limit: $limit) {
                id qid name price views images
            }
        }
        """
        return self.client.execute(query, {'limit': limit}).get('FindTopViewedProducts', [])
    
    # ========== التحويرات ==========
    
    def create(self, input_data: Dict) -> Optional[Dict]:
        query = """
        mutation($input: CreateProductInput!) {
            createProduct(input: $input) {
                id qid name price status createdAt
            }
        }
        """
        return self.client.execute(query, {'input': input_data}).get('createProduct')
    
    def update(self, qid: str, input_data: Dict) -> Optional[Dict]:
        query = """
        mutation($qid: String!, $input: UpdateProductInfoInput!) {
            updateProductInfo(qid: $qid, input: $input) {
                id qid name price updatedAt
            }
        }
        """
        return self.client.execute(query, {'qid': qid, 'input': input_data}).get('updateProductInfo')
    
    def update_status(self, qid: str, status: str) -> Optional[Dict]:
        query = """
        mutation($qid: String!, $status: String!) {
            updateProductStatus(qid: $qid, status: $status) {
                id qid status updatedAt
            }
        }
        """
        return self.client.execute(query, {'qid': qid, 'status': status}).get('updateProductStatus')
    
    def update_price(self, qid: str, price: float, compare_at_price: float = None) -> Optional[Dict]:
        query = """
        mutation($qid: String!, $price: Float!, $compareAtPrice: Float) {
            updateProductPricing(qid: $qid, price: $price, compareAtPrice: $compareAtPrice) {
                id qid price compareAtPrice updatedAt
            }
        }
        """
        variables = {'qid': qid, 'price': price}
        if compare_at_price is not None:
            variables['compareAtPrice'] = compare_at_price
        return self.client.execute(query, variables).get('updateProductPricing')
    
    def update_images(self, qid: str, images: List[str]) -> Optional[Dict]:
        query = """
        mutation($qid: String!, $images: [String!]!) {
            updateProductImages(qid: $qid, images: $images) {
                id qid images updatedAt
            }
        }
        """
        return self.client.execute(query, {'qid': qid, 'images': images}).get('updateProductImages')
    
    def update_seo(self, qid: str, seo: Dict) -> Optional[Dict]:
        query = """
        mutation($qid: String!, $seo: SEOInput!) {
            updateProductSEO(qid: $qid, seo: $seo) {
                id qid seo { title description keywords } updatedAt
            }
        }
        """
        return self.client.execute(query, {'qid': qid, 'seo': seo}).get('updateProductSEO')
    
    def update_dimensions(self, qid: str, dimensions: Dict) -> Optional[Dict]:
        query = """
        mutation($qid: String!, $dimensions: DimensionsInput!) {
            updateProductDimensions(qid: $qid, dimensions: $dimensions) {
                id qid dimensions { length width height } updatedAt
            }
        }
        """
        return self.client.execute(query, {'qid': qid, 'dimensions': dimensions}).get('updateProductDimensions')
    
    def update_weight(self, qid: str, weight: float) -> Optional[Dict]:
        query = """
        mutation($qid: String!, $weight: Float!) {
            updateProductWeight(qid: $qid, weight: $weight) {
                id qid weight updatedAt
            }
        }
        """
        return self.client.execute(query, {'qid': qid, 'weight': weight}).get('updateProductWeight')
    
    def update_description(self, qid: str, description: str) -> Optional[Dict]:
        query = """
        mutation($qid: String!, $description: String!) {
            updateProductDescription(qid: $qid, description: $description) {
                id qid description updatedAt
            }
        }
        """
        return self.client.execute(query, {'qid': qid, 'description': description}).get('updateProductDescription')
    
    def update_collections(self, qid: str, collection_qids: List[str]) -> Optional[Dict]:
        query = """
        mutation($qid: String!, $collectionQids: [String!]!) {
            updateProductCollection(qid: $qid, collectionQids: $collectionQids) {
                id qid collections { id name }
            }
        }
        """
        return self.client.execute(query, {'qid': qid, 'collectionQids': collection_qids}).get('updateProductCollection')
    
    def delete(self, qid: str) -> bool:
        query = "mutation($qid: String!) { deleteProduct(qid: $qid) }"
        result = self.client.execute(query, {'qid': qid})
        return result.get('deleteProduct', False) if result else False
    
    def bulk_delete(self, qids: List[str]) -> bool:
        query = "mutation($qids: [String!]!) { bulkDeleteProduct(qids: $qids) }"
        result = self.client.execute(query, {'qids': qids})
        return result.get('bulkDeleteProduct', False) if result else False
    
    def bulk_update_status(self, qids: List[str], status: str) -> List[Dict]:
        query = """
        mutation($qids: [String!]!, $status: String!) {
            bulkUpdateProductsStatus(qids: $qids, status: $status) {
                id qid status updatedAt
            }
        }
        """
        return self.client.execute(query, {'qids': qids, 'status': status}).get('bulkUpdateProductsStatus', [])
