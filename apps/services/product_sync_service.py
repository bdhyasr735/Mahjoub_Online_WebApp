# coding: utf-8
# 📂 apps/services/product_sync_service.py

import requests
from apps.services.update_product_data import UPDATE_PRODUCT_MUTATION

GRAPHQL_ENDPOINT = "https://mahjoub.online/admin/graphql"

# ✅ استعلام إضافة منتج جديد
CREATE_PRODUCT_MUTATION = """
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

# ✅ الاستعلام المعدل - تم إزالة حقل sku
GET_PRODUCT_DETAIL_QUERY = """
query($qid: String!) {
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
            }
            images {
                _id
                fileUrl
            }
            collections {
                qid
                title
                slug
            }
            variants {
                _id
                quantity
                pricing {
                    price
                    compareAtPrice
                }
            }
        }
    }
}
"""

class ProductSyncService:
    def __init__(self, token: str):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    # ============================================================
    # ✅ إضافة منتج جديد (مسودة - DRAFT)
    # ============================================================
    def create_product(self, product_data: dict) -> dict:
        """
        إنشاء منتج جديد في قمرة (حالة DRAFT)
        
        Args:
            product_data: بيانات المنتج {
                'title': str,
                'description': str,
                'price': float,
                'quantity': int,
                'images': list,  # قائمة روابط الصور
                'supplier_id': str,  # معرف المورد في قمرة
                'collections': list  # قائمة معرفات المجموعات
            }
        
        Returns:
            dict: {'success': bool, 'qid': str, 'message': str}
        """
        try:
            # ✅ تحضير البيانات للإرسال
            input_data = {
                "title": product_data.get('title', ''),
                "description": product_data.get('description', ''),
                "status": "DRAFT",  # ✅ دائماً مسودة
                "pricing": {
                    "price": float(product_data.get('price', 0))
                },
                "quantity": int(product_data.get('quantity', 0)),
                "supplierId": product_data.get('supplier_id', '')
            }
            
            # ✅ إضافة الصور إن وجدت
            if product_data.get('images'):
                input_data["images"] = product_data['images']
            
            # ✅ إضافة المجموعات إن وجدت
            if product_data.get('collections'):
                input_data["collections"] = product_data['collections']
            
            response = requests.post(
                GRAPHQL_ENDPOINT,
                headers=self.headers,
                json={
                    "query": CREATE_PRODUCT_MUTATION,
                    "variables": {"input": input_data}
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'message': f'HTTP Error {response.status_code}',
                    'qid': None
                }
            
            result = response.json()
            
            if 'errors' in result:
                return {
                    'success': False,
                    'message': str(result['errors']),
                    'qid': None
                }
            
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
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Request Error: {str(e)}',
                'qid': None
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'qid': None
            }

    # ============================================================
    # ✅ تحديث حالة المنتج
    # ============================================================
    def update_product_status(self, qid: str, status: str) -> bool:
        """
        تحديث حالة المنتج في قمرة
        
        Args:
            qid: معرف المنتج
            status: الحالة الجديدة (DRAFT, PUBLISHED, REJECTED, ARCHIVED)
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        UPDATE_STATUS_MUTATION = """
        mutation($qid: String!, $status: String!) {
            updateProductStatus(qid: $qid, status: $status) {
                success
                message
            }
        }
        """
        try:
            response = requests.post(
                GRAPHQL_ENDPOINT,
                headers=self.headers,
                json={
                    "query": UPDATE_STATUS_MUTATION,
                    "variables": {"qid": qid, "status": status}
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ HTTP Error: {response.status_code}")
                return False
            
            result = response.json()
            
            if 'errors' in result:
                print(f"❌ GraphQL Errors: {result['errors']}")
                return False
            
            update_result = result.get('data', {}).get('updateProductStatus', {})
            return update_result.get('success', False)
            
        except Exception as e:
            print(f"❌ Error in update_product_status: {e}")
            return False

    # ============================================================
    # ✅ تحديث منتج
    # ============================================================
    def update_product(self, qid: str, product_data: dict) -> bool:
        """
        تحديث منتج موجود في قمرة
        
        Args:
            qid: معرف المنتج
            product_data: بيانات المنتج المحدثة
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        UPDATE_PRODUCT_MUTATION = """
        mutation($qid: String!, $input: UpdateProductInput!) {
            updateProduct(qid: $qid, input: $input) {
                success
                message
            }
        }
        """
        try:
            input_data = {
                "title": product_data.get('title'),
                "description": product_data.get('description'),
                "pricing": {
                    "price": float(product_data.get('price', 0))
                },
                "quantity": int(product_data.get('quantity', 0))
            }
            
            response = requests.post(
                GRAPHQL_ENDPOINT,
                headers=self.headers,
                json={
                    "query": UPDATE_PRODUCT_MUTATION,
                    "variables": {"qid": qid, "input": input_data}
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return False
            
            result = response.json()
            
            if 'errors' in result:
                print(f"❌ GraphQL Errors: {result['errors']}")
                return False
            
            update_result = result.get('data', {}).get('updateProduct', {})
            return update_result.get('success', False)
            
        except Exception as e:
            print(f"❌ Error in update_product: {e}")
            return False

    # ============================================================
    # ✅ حذف منتج
    # ============================================================
    def delete_product(self, qid: str) -> bool:
        """
        حذف منتج من قمرة
        
        Args:
            qid: معرف المنتج
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        DELETE_PRODUCT_MUTATION = """
        mutation($qid: String!) {
            deleteProduct(qid: $qid) {
                success
                message
            }
        }
        """
        try:
            response = requests.post(
                GRAPHQL_ENDPOINT,
                headers=self.headers,
                json={
                    "query": DELETE_PRODUCT_MUTATION,
                    "variables": {"qid": qid}
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return False
            
            result = response.json()
            
            if 'errors' in result:
                print(f"❌ GraphQL Errors: {result['errors']}")
                return False
            
            delete_result = result.get('data', {}).get('deleteProduct', {})
            return delete_result.get('success', False)
            
        except Exception as e:
            print(f"❌ Error in delete_product: {e}")
            return False

    # ============================================================
    # ✅ جلب المنتجات
    # ============================================================
    def fetch_products(self, page: int = 1, limit: int = 50, title: str = ""):
        query = """
        query($page: Int!, $limit: Int!, $title: String) {
            findAllProducts(input: { page: $page, limit: $limit, title: $title }) {
                success
                message
                data {
                    qid
                    title
                    slug
                    description
                    pricing {
                        price
                        compareAtPrice
                    }
                    quantity
                    images {
                        _id
                        fileUrl
                    }
                }
                pagination {
                    totalPages
                    currentPage
                    limit
                }
            }
        }
        """
        variables = {"page": page, "limit": limit}
        if title:
            variables["title"] = title
         
        try:
            response = requests.post(
                GRAPHQL_ENDPOINT,
                headers=self.headers,
                json={"query": query, "variables": variables},
                timeout=30
            )
            if response.status_code != 200:
                print(f"findAllProducts HTTP Error {response.status_code}: {response.text}")
                return {"data": [], "pagination": None}

            result = response.json()
            if "errors" in result or "data" not in result or "findAllProducts" not in result["data"]:
                print(f"findAllProducts GraphQL Errors/Missing Data: {result}")
                return {"data": [], "pagination": None}

            return result["data"]["findAllProducts"]
        except requests.exceptions.RequestException as e:
            print(f"Request Exception in fetch_products: {str(e)}")
            return {"data": [], "pagination": None}

    # ============================================================
    # ✅ جلب منتج بواسطة QID
    # ============================================================
    def fetch_product_by_qid(self, qid: str):
        variables = {"qid": qid}
        try:
            response = requests.post(
                GRAPHQL_ENDPOINT,
                headers=self.headers,
                json={"query": GET_PRODUCT_DETAIL_QUERY, "variables": variables},
                timeout=30
            )
            if response.status_code != 200:
                print(f"GraphQL HTTP Error: {response.status_code}")
                print(f"Response Body: {response.text}")
                return None

            result = response.json()
            if "errors" in result:
                print("GraphQL Errors in fetch_product_by_qid:", result["errors"])
                return None

            if "data" not in result or "findProductByQid" not in result["data"]:
                print("GraphQL Response missing data fields:", result)
                return None

            res_data = result["data"]["findProductByQid"]
            if res_data and res_data.get("success"):
                return res_data.get("data")
             
            print("GraphQL findProductByQid returned success=False:", res_data)
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request Exception in fetch_product_by_qid: {str(e)}")
            return None

    # ============================================================
    # ✅ جلب المجموعات
    # ============================================================
    def fetch_collections(self):
        query = """
        query {
            findAllCollections(input: { page: 1, limit: 100 }) {
                success
                message
                data {
                    qid
                    title
                    slug
                }
            }
        }
        """
        try:
            response = requests.post(
                GRAPHQL_ENDPOINT,
                headers=self.headers,
                json={"query": query},
                timeout=30
            )
            if response.status_code != 200:
                return []
            
            result = response.json()
            col_res = result.get("data", {}).get("findAllCollections")
            if isinstance(col_res, dict) and col_res.get("success"):
                return col_res.get("data", [])
            elif isinstance(col_res, list):
                return col_res
            return []
        except Exception as e:
            print(f"Error fetching collections: {e}")
            return []

    # ============================================================
    # ✅ تحديث بيانات المنتج
    # ============================================================
    def update_product_data(self, qid: str, info: dict, pricing: dict, dims: dict, weight: dict, ident: dict, desc: str, **kwargs):
        variables = {
            "id": qid,
            "info": info,
            "pricing": pricing,
            "dims": dims,
            "weight": weight,
            "ident": ident,
            "desc": desc
        }
        if kwargs:
            variables.update(kwargs)
         
        try:
            response = requests.post(
                GRAPHQL_ENDPOINT,
                headers=self.headers,
                json={"query": UPDATE_PRODUCT_MUTATION, "variables": variables},
                timeout=30
            )
            if response.status_code != 200:
                print(f"Update HTTP Error {response.status_code}: {response.text}")
                return False

            result = response.json()
            if "errors" in result:
                print("Update Errors:", result["errors"])
                return False

            return True
        except requests.exceptions.RequestException as e:
            print(f"Request Exception in update_product_data: {str(e)}")
            return False

    # ============================================================
    # ✅ مزامنة مع قاعدة البيانات المحلية
    # ============================================================
    def sync_to_local_db(self, products_data):
        if not products_data or "data" not in products_data:
            return
        for product in products_data.get("data", []):
            print(f"Fetched product {product.get('qid')} - {product.get('title')}")
