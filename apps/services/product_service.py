# coding: utf-8
# 📦 خدمة المنتجات - منصة محجوب أونلاين 2026

import os
from apps.services.graphql_client import GraphQLClient


class ProductService:
    """خدمة إدارة المنتجات متصلة بملف الاستعلامات الخارجي product_queries.graphql"""
    
    def __init__(self, client=None):
        """
        تهيئة خدمة المنتجات
        
        Args:
            client (GraphQLClient, optional): عميل GraphQL. إذا لم يتم توفيره، يتم إنشاء عميل جديد.
        """
        # ✅ استخدام العميل الممرر أو إنشاء عميل جديد
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
        # ✅ استعلام مبسط للاختبار
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
        query = """
        query($qid: String!) {
            findProductByQid(qid: $qid) {
                id
                qid
                name
                price
                status
                description
            }
        }
        """
        
        variables = {"qid": qid}
        
        try:
            data = self.client.execute(query, variables)
            if data and "findProductByQid" in data:
                return data["findProductByQid"]
            return None
        except Exception as e:
            print(f"❌ [ProductService]: خطأ في جلب المنتج {qid}: {e}")
            return None

    def get_product_status(self) -> list:
        """جلب حالة المنتجات"""
        query = """
        query {
            findProductStatus {
                id
                qid
                name
                status
                isActive
            }
        }
        """
        
        try:
            data = self.client.execute(query)
            if data and "findProductStatus" in data:
                return data["findProductStatus"]
            return []
        except Exception as e:
            print(f"❌ [ProductService]: خطأ في جلب حالة المنتجات: {e}")
            return []

    def get_top_viewed_products(self) -> list:
        """جلب المنتجات الأكثر مشاهدة"""
        query = """
        query {
            FindTopViewedProducts {
                id
                qid
                name
                price
                views
            }
        }
        """
        
        try:
            data = self.client.execute(query)
            if data and "FindTopViewedProducts" in data:
                return data["FindTopViewedProducts"]
            return []
        except Exception as e:
            print(f"❌ [ProductService]: خطأ في جلب المنتجات الأكثر مشاهدة: {e}")
            return []

    def create_product_data(self, input_data: dict) -> dict:
        """إنشاء منتج جديد عبر الـ Mutation"""
        query = """
        mutation($input: CreateProductInput!) {
            createProduct(input: $input) {
                id
                qid
                name
                price
                status
            }
        }
        """
        
        variables = {"input": input_data}
        
        try:
            data = self.client.execute(query, variables)
            if data and "createProduct" in data:
                return data["createProduct"]
            return {}
        except Exception as e:
            print(f"❌ [ProductService]: خطأ في إنشاء المنتج: {e}")
            return {}

    def update_product_data(self, input_data: dict) -> dict:
        """تعديل بيانات منتج عبر الـ Mutation"""
        query = """
        mutation($input: UpdateProductInput!) {
            updateProduct(input: $input) {
                id
                qid
                name
                price
                status
            }
        }
        """
        
        variables = {"input": input_data}
        
        try:
            data = self.client.execute(query, variables)
            if data and "updateProduct" in data:
                return data["updateProduct"]
            return {}
        except Exception as e:
            print(f"❌ [ProductService]: خطأ في تعديل المنتج: {e}")
            return {}
