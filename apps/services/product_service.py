# coding: utf-8
# 📦 خدمة المنتجات - منصة محجوب أونلاين 2026

import os
from apps.services.graphql_client import GraphQLClient


class ProductService:
    """خدمة إدارة المنتجات متصلة بهيكل استجابات GraphQL المحدث"""
    
    def __init__(self, client=None):
        self.client = client if client else GraphQLClient()
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.query_file_path = os.path.join(current_dir, 'product_queries.graphql')
        
        try:
            with open(self.query_file_path, 'r', encoding='utf-8') as f:
                self.queries_content = f.read()
        except FileNotFoundError:
            self.queries_content = ""

    def get_all_products(self, input_data: dict = None) -> list:
        """جلب جميع المنتجات مع دعم الترقيم والفلترة"""
        query = """
        query FindAllProducts($input: GetAllProductsInput) {
            findAllProducts(input: $input) {
                success
                message
                data {
                    id
                    qid
                    name
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
        
        variables = {"input": input_data} if input_data else {}
        
        try:
            data = self.client.execute(query, variables, operation_name="FindAllProducts")
            if data and "findAllProducts" in data:
                result_obj = data["findAllProducts"]
                if result_obj.get("success"):
                    return result_obj.get("data", [])
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
                    id
                    qid
                    name
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
                result_obj = data["findProductByQid"]
                if result_obj.get("success"):
                    return result_obj.get("data", {})
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
