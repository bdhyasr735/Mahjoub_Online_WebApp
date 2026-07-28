# coding: utf-8
# 📦 خدمة المنتجات - منصة محجوب أونلاين 2026

import os
import re
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

    def _extract_query(self, query_name: str) -> str:
        """استخراج استعلام معين من ملف الاستعلامات"""
        if not self.queries_content:
            return ""
        
        lines = self.queries_content.split('\n')
        result = []
        found = False
        brace_count = 0
        
        for line in lines:
            if f"query {query_name}" in line or f"mutation {query_name}" in line:
                found = True
            
            if found:
                result.append(line)
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0 and len(result) > 1:
                    break
        
        return '\n'.join(result)

    def get_all_products(self, input_data: dict = None) -> dict:
        """جلب جميع المنتجات مع معلومات الترقيم"""
        query = """
        {
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

    def get_products_page(self, page: int = 1) -> dict:
        """جلب صفحة محددة من المنتجات"""
        query = """
        query($page: Int!) {
            findAllProducts(input: { page: $page }) {
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
            variables = {"page": page}
            data = self.client.execute(query, variables)
            if data and "findAllProducts" in data:
                return data["findAllProducts"]
            return {}
        except Exception as e:
            print(f"❌ [ProductService]: {e}")
            return {}

    def fetch_all_products_for_search(self, max_pages: int = 10) -> list:
        """جلب المنتجات من أول 10 صفحات للبحث مع Cache"""
        if hasattr(self, '_search_cache') and self._search_cache is not None:
            print(f"✅ [ProductService]: استخدام Cache (عدد {len(self._search_cache)} منتج)")
            return self._search_cache
        
        all_products = []
        page = 1
        has_next = True
        
        print(f"🔄 [ProductService]: جاري جلب {max_pages} صفحة للبحث...")
        
        while has_next and page <= max_pages:
            try:
                result = self.get_products_page(page)
                products = result.get('data', [])
                pagination = result.get('pagination', {})
                
                all_products.extend(products)
                has_next = pagination.get('hasNextPage', False)
                
                print(f"📄 [ProductService]: تم جلب صفحة {page} ({len(products)} منتج)")
                page += 1
                
            except Exception as e:
                print(f"❌ [ProductService]: خطأ في جلب الصفحة {page}: {e}")
                break
        
        self._search_cache = all_products
        print(f"✅ [ProductService]: تم تخزين {len(all_products)} منتج في Cache")
        return all_products
    
    def clear_search_cache(self):
        """مسح Cache البحث"""
        self._search_cache = None
        print(f"🔄 [ProductService]: تم مسح Cache البحث")

    def get_product_by_qid(self, qid: str) -> dict:
        """جلب منتج بواسطة QID مع جميع الحقول باستخدام متغيرات GraphQL"""
        query = """
        query($qid: String!) {
            findProductByQid(qid: $qid) {
                success
                message
                data {
                    qid
                    title
                    description
                    status
                    pricing {
                        price
                        compareAtPrice
                    }
                    images {
                        fileUrl
                    }
                    quantity
                    seo {
                        title
                        description
                        keywords
                    }
                    tags
                    collections {
                        title
                    }
                    variants {
                        _id
                        qid
                        quantity
                        pricing {
                            price
                            compareAtPrice
                        }
                        options {
                            label
                        }
                        images {
                            _id
                            fileUrl
                            path
                        }
                    }
                    options {
                        qid
                        name
                        values {
                            option
                            label
                            sortOrder
                        }
                    }
                    slug
                    views
                    publishedAt
                }
            }
        }
        """
        
        try:
            variables = {"qid": qid}
            print(f"🔍 [get_product_by_qid] جلب المنتج بـ QID: {qid}")
            
            data = self.client.execute(query, variables)
            print(f"🔍 [get_product_by_qid] Full Response: {data}")
            
            if data and "findProductByQid" in data:
                result = data["findProductByQid"]
                if result.get("success"):
                    product_data = result.get("data", {})
                    print(f"✅ [get_product_by_qid] تم جلب المنتج: {product_data.get('title')}")
                    return product_data
                else:
                    error_msg = result.get('message', 'خطأ غير معروف')
                    print(f"❌ [get_product_by_qid] فشل جلب المنتج - {error_msg}")
                    return {}
            return {}
                
        except Exception as e:
            print(f"❌ [get_product_by_qid] Exception: {e}")
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
