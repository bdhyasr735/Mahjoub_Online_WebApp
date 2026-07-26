# coding: utf-8
# 📦 خدمة المنتجات - منصة محجوب أونلاين 2026

import os
from apps.services.graphql_client import GraphQLClient


class ProductService:
    """خدمة إدارة المنتجات متصلة بملف الاستعلامات الخارجي product_queries.graphql"""
    
    def __init__(self):
        self.client = GraphQLClient()
        
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
        if not self.queries_content:
            return []

        # ✅ استعلام مبسط بدون input
        query = """
        query {
            findAllProducts {
                id
                qid
                name
                price
                status
            }
        }
        """
        
        try:
            data = self.client.execute(query)
            if data and "findAllProducts" in data:
                return data["findAllProducts"]
            return []
        except Exception as e:
            print(f"❌ [ProductService]: خطأ في جلب المنتجات: {e}")
            return []

    def get_product_by_qid(self, qid: str) -> dict:
        """جلب منتج معين بواسطة الـ Qid"""
        if not self.queries_content:
            return None

        variables = {"qid": qid}
        data = self.client.execute(
            query=self.queries_content,
            variables=variables,
            operation_name="FindProductByQid"
        )
        
        if data and "findProductByQid" in data:
            return data["findProductByQid"]
        return None

    def get_product_status(self) -> list:
        """جلب حالة المنتجات"""
        if not self.queries_content:
            return []

        data = self.client.execute(
            query=self.queries_content,
            operation_name="FindProductStatus"
        )
        
        if data and "findProductStatus" in data:
            return data["findProductStatus"]
        return []

    def get_top_viewed_products(self) -> list:
        """جلب المنتجات الأكثر مشاهدة"""
        if not self.queries_content:
            return []

        data = self.client.execute(
            query=self.queries_content,
            operation_name="FindTopViewedProducts"
        )
        
        if data and "FindTopViewedProducts" in data:
            return data["FindTopViewedProducts"]
        return []

    def create_product_data(self, input_data: dict) -> dict:
        """إنشاء منتج جديد عبر الـ Mutation الموجودة في الملف"""
        if not self.queries_content:
            return None

        variables = {"input": input_data}
        data = self.client.execute(
            query=self.queries_content,
            variables=variables,
            operation_name="CreateProduct"
        )
        
        if data and "createProduct" in data:
            return data["createProduct"]
        return {}

    def update_product_data(self, input_data: dict) -> dict:
        """تعديل بيانات منتج عبر الـ Mutation الموجودة في الملف"""
        if not self.queries_content:
            return None

        variables = {"input": input_data}
        data = self.client.execute(
            query=self.queries_content,
            variables=variables,
            operation_name="UpdateProduct"
        )
        
        if data and "updateProduct" in data:
            return data["updateProduct"]
        return {}
