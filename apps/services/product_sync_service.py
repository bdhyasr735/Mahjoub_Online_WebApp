# coding: utf-8
# 📂 apps/services/product_sync_service.py

from apps.services.graphql_client import QomrahGraphQLClient

class ProductSyncService:
    def __init__(self, token: str):
        self.token = token
        self.client = QomrahGraphQLClient()

    def create_product(self, product_data: dict) -> dict:
        """إنشاء منتج جديد في قمرة"""
        mutation = """
        mutation($input: CreateProductInput!) {
            createProduct(input: $input) {
                success
                message
                data {
                    qid
                    title
                    status
                }
            }
        }
        """
        
        input_data = {
            "title": product_data.get('title', ''),
            "description": product_data.get('description', ''),
            "status": "DRAFT",
            "pricing": {
                "price": float(product_data.get('price', 0))
            },
            "quantity": int(product_data.get('quantity', 0)),
            "supplierId": product_data.get('supplier_id', ''),
            "images": product_data.get('images', [])
        }
        
        result = self.client.execute_query(mutation, {"input": input_data})
        
        if result:
            create_result = result.get('data', {}).get('createProduct', {})
            if create_result.get('success'):
                data = create_result.get('data', {})
                return {
                    'success': True,
                    'qid': data.get('qid'),
                    'message': create_result.get('message', 'تم إنشاء المنتج بنجاح')
                }
            else:
                return {
                    'success': False,
                    'message': create_result.get('message', 'فشل إنشاء المنتج'),
                    'qid': None
                }
        else:
            return {
                'success': False,
                'message': 'فشل الاتصال بقمرة',
                'qid': None
            }
