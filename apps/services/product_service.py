# coding: utf-8
# 📦 خدمة المنتجات - منصة محجوب أونلاين 2026

import os
from apps.services.graphql_client import GraphQLClient


class ProductService:
    """خدمة إدارة المنتجات متصلة بهيكل استجابات GraphQL المحدث"""
    
    def __init__(self, client=None):
        """
        تهيئة خدمة المنتجات
        
        Args:
            client (GraphQLClient, optional): عميل GraphQL. إذا لم يتم توفيره، يتم إنشاء عميل جديد.
        """
        self.client = client if client else GraphQLClient()
        
        # قراءة ملف product_queries.graphql الخارجي تلقائياً من نفس المجلد
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.query_file_path = os.path.join(current_dir, 'product_queries.graphql')
        
        try:
            with open(self.query_file_path, 'r', encoding='utf-8') as f:
                self.queries_content = f.read()
        except FileNotFoundError:
            print(f"⚠️ [ProductService]: لم يتم العثور على ملف الاستعلامات في المسار: {self.query_file_path}")
            self.queries_content = ""

    def get_all_products(self, input_data: dict = None) -> list:
        """جلب جميع المنتجات"""
        query = """
        query FindAllProducts {
            findAllProducts {
                success
                message
                data {
                    qid
                    title
                    price
                    status
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
            data = self.client.execute(query, operation_name="FindAllProducts")
            if data and "findAllProducts" in data:
                result = data["findAllProducts"]
                if result.get("success"):
                    return result.get("data", [])
            return []
        except Exception as e:
            print(f"❌ [ProductService]: خطأ في جلب المنتجات: {e}")
            return []

    def get_product_by_qid(self, qid: str) -> dict:
        """جلب منتج معين بواسطة الـ Qid"""
        query = """
        query FindProductByQid($qid: String!) {
            findProductByQid(qid: $qid) {
                success
                message
                data {
                    qid
                    title
                    price
                    status
                    description
                }
            }
        }
        """
        
        variables = {"qid": qid}
        
        try:
            data = self.client.execute(query, variables, operation_name="FindProductByQid")
            if data and "findProductByQid" in data:
                result = data["findProductByQid"]
                if result.get("success"):
                    return result.get("data", {})
            return {}
        except Exception as e:
            print(f"❌ [ProductService]: خطأ في جلب المنتج {qid}: {e}")
            return {}

    def get_product_status(self) -> dict:
        """جلب حالة المنتجات"""
        query = """
        query FindProductStatus {
            findProductStatus {
                success
                message
                data
            }
        }
        """
        
        try:
            data = self.client.execute(query, operation_name="FindProductStatus")
            if data and "findProductStatus" in data:
                return data["findProductStatus"]
            return {}
        except Exception as e:
            print(f"❌ [ProductService]: خطأ في جلب حالة المنتجات: {e}")
            return {}

    def create_product_data(self, input_data: dict) -> dict:
        """إنشاء منتج جديد عبر الـ Mutation"""
        query = """
        mutation CreateProduct($input: CreateProductInput!) {
            createProduct(input: $input) {
                success
                message
                data {
                    qid
                    title
                    price
                    status
                }
            }
        }
        """
        
        variables = {"input": input_data}
        
        try:
            data = self.client.execute(query, variables, operation_name="CreateProduct")
            if data and "createProduct" in data:
                result = data["createProduct"]
                if result.get("success"):
                    return result.get("data", {})
            return {}
        except Exception as e:
            print(f"❌ [ProductService]: خطأ في إنشاء المنتج: {e}")
            return {}

    def update_product_data(self, input_data: dict) -> dict:
        """تعديل بيانات منتج عبر الـ Mutation"""
        query = """
        mutation UpdateProduct($input: UpdateProductInput!) {
            updateProduct(input: $input) {
                success
                message
                data {
                    qid
                    title
                    price
                    status
                }
            }
        }
        """
        
        variables = {"input": input_data}
        
        try:
            data = self.client.execute(query, variables, operation_name="UpdateProduct")
            if data and "updateProduct" in data:
                result = data["updateProduct"]
                if result.get("success"):
                    return result.get("data", {})
            return {}
        except Exception as e:
            print(f"❌ [ProductService]: خطأ في تعديل المنتج: {e}")
            return {}
