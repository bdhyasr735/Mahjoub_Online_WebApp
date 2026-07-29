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
        """جلب جميع المنتجات مع معلومات الترقيم والأسعار والـ slug (باستخدام الصفحة الأولى افتراضياً)"""
        return self.get_products_page(page=1)

    def get_products_page(self, page: int = 1) -> dict:
        """جلب صفحة محددة من المنتجات مع الأسعار والـ slug وتمرير المتغيرات بشكل آمن"""
        query = """
        query($page: Int!) {
            findAllProducts(input: { page: $page }) {
                success
                message
                data {
                    qid
                    title
                    slug
                    description
                    status
                    pricing {
                        price
                        compareAtPrice
                        originalPrice
                        discount {
                            discountValue
                            discountType
                        }
                    }
                    images {
                        fileUrl
                    }
                    quantity
                    variants {
                        qid
                        pricing {
                            price
                            compareAtPrice
                            originalPrice
                        }
                    }
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
            safe_page = int(page) if page and str(page).isdigit() else 1
            variables = {"page": safe_page}
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
        """جلب منتج بواسطة QID مع تفاصيل الأسعار والـ slug والكمية والمجموعات (النسخة الآمنة والموثوقة)"""
        
        # ✅ تم إزالة أي حقول إضافية قد ترفضها الساندبوكس
        query = """
        query FindProductByQid($qid: String!) {
            findProductByQid(qid: $qid) {
                success
                message
                data {
                    qid
                    title
                    slug
                    description
                    status
                    quantity
                    pricing {
                        price
                        compareAtPrice
                        originalPrice
                        discount {
                            discountValue
                            discountType
                        }
                    }
                    images {
                        fileUrl
                    }
                    seo {
                        title
                        description
                        keywords
                    }
                    tags
                    collections {
                        title
                        handle
                    }
                    variants {
                        _id
                        qid
                        quantity
                        pricing {
                            price
                            compareAtPrice
                            originalPrice
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
                    # ✅ هذا هو الجزء الوحيد الذي تم إبقاؤه لجلب الخيارات
                    options {
                        qid
                        name
                        values {
                            option
                            label
                            sortOrder
                        }
                    }
                    views
                    publishedAt
                }
            }
        }
        """
        
        try:
            print(f"🔍 [get_product_by_qid] جلب المنتج بـ QID: {qid}")
            
            variables = {"qid": qid}
            print(f"🔍 [get_product_by_qid] Variables: {variables}")
            
            data = self.client.execute(query, variables, operation_name="FindProductByQid")
            print(f"🔍 [get_product_by_qid] Full Response: {data}")
            
            if data and "findProductByQid" in data:
                result = data["findProductByQid"]
                if result.get("success"):
                    product_data = result.get("data", {})
                    print(f"✅ [get_product_by_qid] تم جلب المنتج: {product_data.get('title')}")
                    print(f"✅ [get_product_by_qid] Quantity: {product_data.get('quantity')}")
                    print(f"✅ [get_product_by_qid] Collections: {product_data.get('collections')}")
                    return product_data
                else:
                    error_msg = result.get('message', 'خطأ غير معروف')
                    print(f"❌ [get_product_by_qid] فشل جلب المنتج - {error_msg}")
                    return {}
            return {}
                
        except Exception as e:
            print(f"❌ [get_product_by_qid] Exception: {e}")
            import traceback
            traceback.print_exc()
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
                    slug
                    pricing {
                        price
                        compareAtPrice
                        originalPrice
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
                    slug
                    pricing {
                        price
                        compareAtPrice
                        originalPrice
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
