# coding: utf-8
# 📂 apps/services/product_sync_service.py

from apps.services.graphql_client import QomrahGraphQLClient
import requests
import os

class ProductSyncService:
    def __init__(self):
        self.client = QomrahGraphQLClient()

    # ============================================================
    # ✅ رفع صورة إلى قمرة
    # ============================================================
    def upload_image(self, image_data: bytes, filename: str) -> str:
        """
        رفع صورة إلى مكتبة قمرة
        
        Args:
            image_data: بيانات الصورة (bytes)
            filename: اسم الملف
        
        Returns:
            str: رابط الصورة في قمرة
        """
        try:
            # ✅ تحضير الملف للرفع
            files = {
                'file': (filename, image_data, 'image/jpeg'),
                'filename': (None, filename)
            }
            
            # ✅ إضافة رأس Authorization
            api_key = os.environ.get('QUMRA_API_KEY')
            if not api_key:
                print("❌ QUMRA_API_KEY غير موجود")
                return None
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Accept': 'application/json'
            }
            
            # ✅ رفع الصورة إلى قمرة
            response = requests.post(
                'https://mahjoub.online/admin/graphql',
                files=files,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                upload_result = result.get('data', {}).get('uploadFile', {})
                if upload_result.get('success'):
                    file_url = upload_result.get('data', {}).get('fileUrl')
                    print(f"✅ تم رفع الصورة بنجاح: {file_url}")
                    return file_url
                else:
                    print(f"❌ فشل رفع الصورة: {upload_result.get('message')}")
                    return None
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ خطأ في رفع الصورة: {e}")
            return None

    # ============================================================
    # ✅ جلب المنتجات
    # ============================================================
    def fetch_products(self, page: int = 1, limit: int = 50, title: str = ""):
        """جلب قائمة المنتجات من قمرة"""
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

        result = self.client.execute_query(query, variables)
        
        if result:
            data = result.get('data', {}).get('findAllProducts', {})
            return {
                "data": data.get('data', []),
                "pagination": data.get('pagination', {"currentPage": page, "totalPages": 1, "limit": limit})
            }
        return {"data": [], "pagination": None}

    # ============================================================
    # ✅ جلب منتج بواسطة QID
    # ============================================================
    def fetch_product_by_qid(self, qid: str):
        """جلب منتج محدد من قمرة بواسطة QID"""
        query = """
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
        result = self.client.execute_query(query, {"qid": qid})
        
        if result:
            data = result.get('data', {}).get('findProductByQid', {})
            if data.get('success'):
                return data.get('data')
        return None

    # ============================================================
    # ✅ جلب المجموعات
    # ============================================================
    def fetch_collections(self):
        """جلب قائمة المجموعات من قمرة"""
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
        result = self.client.execute_query(query)
        
        if result:
            data = result.get('data', {}).get('findAllCollections', {})
            if data.get('success'):
                return data.get('data', [])
        return []

    # ============================================================
    # ✅ إنشاء منتج
    # ============================================================
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

    # ============================================================
    # ✅ تحديث حالة المنتج
    # ============================================================
    def update_product_status(self, qid: str, status: str) -> bool:
        """تحديث حالة المنتج في قمرة"""
        mutation = """
        mutation($qid: String!, $status: String!) {
            updateProductStatus(qid: $qid, status: $status) {
                success
                message
            }
        }
        """
        result = self.client.execute_query(mutation, {"qid": qid, "status": status})
        
        if result:
            update_result = result.get('data', {}).get('updateProductStatus', {})
            return update_result.get('success', False)
        return False

    # ============================================================
    # ✅ حذف المنتج
    # ============================================================
    def delete_product(self, qid: str) -> bool:
        """حذف منتج من قمرة"""
        mutation = """
        mutation($qid: String!) {
            deleteProduct(qid: $qid) {
                success
                message
            }
        }
        """
        result = self.client.execute_query(mutation, {"qid": qid})
        
        if result:
            delete_result = result.get('data', {}).get('deleteProduct', {})
            return delete_result.get('success', False)
        return False

    # ============================================================
    # ✅ تحديث بيانات المنتج
    # ============================================================
    def update_product_data(self, qid: str, **kwargs):
        """تحديث بيانات المنتج في قمرة"""
        info = kwargs.get('info', {})
        pricing = kwargs.get('pricing', {})
        weight = kwargs.get('weight', {})
        ident = kwargs.get('ident', {})
        description = kwargs.get('desc', '')
        
        mutation = """
        mutation($qid: String!, $info: UpdateProductInfo!, $pricing: PricingInput!, $weight: WeightInput!, $ident: IdentificationInput!, $desc: String!) {
            updateProductInfo(id: $qid, updateProductInfoInput: $info) { success }
            updateProductPricing(id: $qid, pricing: $pricing) { success }
            updateProductWeight(id: $qid, data: $weight) { success }
            updateProductIdentification(id: $qid, data: $ident) { success }
            updateProductDescription(id: $qid, data: $desc) { success }
        }
        """
        
        variables = {
            "qid": qid,
            "info": info,
            "pricing": pricing,
            "weight": weight,
            "ident": ident,
            "desc": description
        }
        
        result = self.client.execute_query(mutation, variables)
        
        if result:
            return True
        return False
