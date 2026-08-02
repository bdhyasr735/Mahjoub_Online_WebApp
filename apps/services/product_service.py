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
        """جلب صفحة محددة من المنتجات مع الأسعار والـ slug وتمرير المتغيرات بشكل آمن (مع معالجة الأخطاء لمنع 500)"""
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
            
            if data and isinstance(data, dict) and "findAllProducts" in data:
                result = data["findAllProducts"]
                if result:
                    return result
            
            return {"data": [], "pagination": {"totalItems": 0, "totalPages": 1, "hasNextPage": False}}
            
        except Exception as e:
            print(f"❌ [ProductService]: {e}")
            return {"data": [], "pagination": {"totalItems": 0, "totalPages": 1, "hasNextPage": False}}

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

    # ✅ الحل الذكي: محاولة جلب المتغيرات، فإن فشل نعود للاستعلام الأساسي
    def get_product_by_qid(self, qid: str) -> dict:
        """جلب منتج بواسطة QID مع محاولة جلب المتغيرات"""
        # الاستعلام المصحح: استخدام fileUrl بدلاً من url
        query_with_variants = """
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
                    # --- المتغيرات بالصيغة الصحيحة (fileUrl) ---
                    variants {
                        qid
                        options {
                            option
                            label
                        }
                        pricing {
                            price
                            compareAtPrice
                        }
                        quantity
                        images {
                            fileUrl
                        }
                    }
                    # ----------------------------------
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
                }
            }
        }
        """
        try:
            print(f"🔍 [get_product_by_qid] محاولة جلب المتغيرات لـ QID: {qid}")
            variables = {"qid": qid}
            data = self.client.execute(query_with_variants, variables, operation_name="FindProductByQid")
            
            if data and "errors" in data:
                print(f"❌ [get_product_by_qid] خطأ GraphQL: {data['errors']}")
            else:
                print(f"✅ [get_product_by_qid] الرد الخام: {data}")

            if data and "findProductByQid" in data:
                result = data["findProductByQid"]
                if result.get("success"):
                    product_data = result.get("data", {})
                    print(f"✅ [get_product_by_qid] تم جلب المنتج بنجاح مع المتغيرات: {product_data.get('title')}")
                    return product_data
                else:
                    print(f"⚠️ [get_product_by_qid] فشل بسبب success=false: {result.get('message')}")
            print(f"⚠️ [get_product_by_qid] لم يتم العثور على المنتج أو حدث خطأ، ننتقل للاستعلام الأساسي...")
            return self._get_product_basic(qid)
        except Exception as e:
            print(f"❌ [get_product_by_qid] استثناء أثناء جلب المتغيرات: {e}")
            return self._get_product_basic(qid)

    def _get_product_basic(self, qid: str) -> dict:
        """جلب المنتج باستخدام استعلام أساسي (بدون المتغيرات)"""
        query_basic = """
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
                }
            }
        }
        """
        try:
            print(f"🔍 [_get_product_basic] جلب المنتج الأساسي لـ QID: {qid}")
            variables = {"qid": qid}
            data = self.client.execute(query_basic, variables, operation_name="FindProductByQid")
            if data and "findProductByQid" in data:
                result = data["findProductByQid"]
                if result.get("success"):
                    product_data = result.get("data", {})
                    print(f"✅ [_get_product_basic] تم جلب المنتج بنجاح: {product_data.get('title')}")
                    return product_data
            return {}
        except Exception as e:
            print(f"❌ [_get_product_basic] فشل جلب المنتج الأساسي: {e}")
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
        """تعديل معلومات المنتج (بدون الحالة - لاستخدام دالة الحالة المنفصلة)"""
        qid = input_data.get('qid')
        if not qid:
            print("❌ [ProductService] qid مفقود في update_product_data")
            return {}

        update_info_input = {k: v for k, v in input_data.items() if k != 'qid'}

        query = """
        mutation UpdateProductInfo($id: String!, $input: UpdateProductInfo!) {
            updateProductInfo(id: $id, updateProductInfoInput: $input) {
                success
                message
            }
        }
        """
        try:
            data = self.client.execute(query, {"id": qid, "input": update_info_input})
            if data and "updateProductInfo" in data:
                return data["updateProductInfo"]
            return {}
        except Exception as e:
            print(f"❌ [ProductService]: خطأ في تحديث المنتج: {e}")
            return {}

    def update_product_status(self, product_qid: str, status: str) -> dict:
        """تحديث حالة المنتج باستخدام updateProductStatus (يتوقع id من نوع ID!)"""
        query = """
        mutation UpdateProductStatus($id: ID!, $status: String!) {
            updateProductStatus(id: $id, status: $status) {
                success
                message
            }
        }
        """
        try:
            data = self.client.execute(query, {"id": product_qid, "status": status})
            if data and "updateProductStatus" in data:
                return data["updateProductStatus"]
            return {}
        except Exception as e:
            print(f"❌ [ProductService]: خطأ في تحديث الحالة: {e}")
            return {}

    def update_product_pricing(self, product_qid: str, pricing_input: dict) -> dict:
        """تحديث تسعير المنتج باستخدام updateProductPricing"""
        query = """
        mutation UpdateProductPricing($id: ID!, $input: UpdateProductPricingInput!) {
            updateProductPricing(id: $id, input: $input) {
                success
                message
            }
        }
        """
        try:
            data = self.client.execute(query, {"id": product_qid, "input": pricing_input})
            if data and "updateProductPricing" in data:
                return data["updateProductPricing"]
            return {}
        except Exception as e:
            print(f"❌ [ProductService]: خطأ في تحديث السعر: {e}")
            return {}
