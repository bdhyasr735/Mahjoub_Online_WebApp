# coding: utf-8
# 📦 خدمة المنتجات - منصة محجوب أونلاين 2026

import os
from apps.services.graphql_client import GraphQLClient


class ProductService:
    """خدمة إدارة المنتجات"""
    
    def __init__(self, client=None):
        self.client = client if client else GraphQLClient()
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.query_file_path = os.path.join(current_dir, 'product_queries.graphql')
        
        try:
            with open(self.query_file_path, 'r', encoding='utf-8') as f:
                self.queries_content = f.read()
        except FileNotFoundError:
            print(f"⚠️ [ProductService]: لم يتم العثور على ملف الاستعلامات")
            self.queries_content = ""

    def get_all_products(self, input_data: dict = None) -> dict:
        """جلب جميع المنتجات مع معلومات الترقيم"""
        query = """
        query {
            findAllProducts {
                success
                message
                data {
                    qid
                    title
                    pricing {
                        price
                        compareAtPrice
                    }
                    status
                    images {
                        fileUrl
                    }
                    quantity
                }
                pagination {
                    totalItems
                    totalPages
                    currentPage
                    limit
                    hasNextPage
                }
            }
        }
        """
        try:
            data = self.client.execute(query)
            if data and "findAllProducts" in data:
                return data["findAllProducts"]
            return {}
        except Exception as e:
            print(f"❌ [ProductService]: {e}")
            return {}

    def get_products_page(self, page: int = 1, limit: int = 10) -> dict:
        """
        جلب صفحة محددة من المنتجات من GraphQL
        
        Args:
            page: رقم الصفحة (يبدأ من 1)
            limit: عدد المنتجات في الصفحة (افتراضي 10)
        
        Returns:
            dict: يحتوي على data و pagination
        """
        # ✅ بما أن الـ API لا يدعم الترقيم، نجلب الكل ثم نقسم
        result = self.get_all_products()
        all_products = result.get('data', [])
        pagination_info = result.get('pagination', {})
        
        # ✅ حساب المؤشرات
        total_items = pagination_info.get('totalItems', len(all_products))
        total_pages = (total_items + limit - 1) // limit if total_items > 0 else 1
        
        # ✅ التأكد من أن الصفحة المطلوبة موجودة
        if page > total_pages:
            page = total_pages
        
        start = (page - 1) * limit
        end = start + limit
        
        # ✅ تقسيم المنتجات
        page_products = all_products[start:end] if all_products else []
        
        return {
            'data': page_products,
            'pagination': {
                'totalItems': total_items,
                'totalPages': total_pages,
                'currentPage': page,
                'limit': limit,
                'hasNextPage': page < total_pages,
                'hasPrevPage': page > 1
            }
        }

    def get_product_by_qid(self, qid: str) -> dict:
        """جلب منتج بواسطة QID"""
        query = """
        query FindProductByQid($qid: String!) {
            findProductByQid(qid: $qid) {
                success
                message
                data {
                    qid
                    title
                    pricing {
                        price
                        compareAtPrice
                    }
                    status
                    description
                    images {
                        fileUrl
                    }
                    quantity
                }
            }
        }
        """
        try:
            data = self.client.execute(query, {"qid": qid})
            if data and "findProductByQid" in data:
                result = data["findProductByQid"]
                if result.get("success"):
                    return result.get("data", {})
            return {}
        except Exception as e:
            print(f"❌ [ProductService]: {e}")
            return {}

    def create_product_data(self, input_data: dict) -> dict:
        """إنشاء منتج جديد"""
        query = """
        mutation CreateProduct($input: CreateProductInput!) {
            createProduct(input: $input) {
                success
                message
                data {
                    qid
                    title
                    pricing {
                        price
                        compareAtPrice
                    }
                    status
                }
            }
        }
        """
        try:
            data = self.client.execute(query, {"input": input_data})
            if data and "createProduct" in data:
                result = data["createProduct"]
                if result.get("success"):
                    return result.get("data", {})
            return {}
        except Exception as e:
            print(f"❌ [ProductService]: {e}")
            return {}

    def update_product_data(self, input_data: dict) -> dict:
        """تعديل منتج"""
        query = """
        mutation UpdateProduct($input: UpdateProductInput!) {
            updateProduct(input: $input) {
                success
                message
                data {
                    qid
                    title
                    pricing {
                        price
                        compareAtPrice
                    }
                    status
                }
            }
        }
        """
        try:
            data = self.client.execute(query, {"input": input_data})
            if data and "updateProduct" in data:
                result = data["updateProduct"]
                if result.get("success"):
                    return result.get("data", {})
            return {}
        except Exception as e:
            print(f"❌ [ProductService]: {e}")
            return {}
