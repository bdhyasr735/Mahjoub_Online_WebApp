# coding: utf-8
# 📂 apps/services/product_sync_service.py

from apps.services.graphql_client import QomrahGraphQLClient
import requests
import os
import base64

class ProductSyncService:
    def __init__(self):
        self.client = QomrahGraphQLClient()

    # ============================================================
    # ✅ رفع صورة إلى قمرة (طريقة GraphQL مع base64)
    # ============================================================
    def upload_image(self, image_data: bytes, filename: str) -> str:
        """
        رفع صورة إلى مكتبة قمرة باستخدام GraphQL Mutation مع base64
        """
        try:
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            image_type = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpeg'
            
            mutation = """
            mutation($file: String!, $filename: String!) {
                uploadFile(file: $file, filename: $filename) {
                    success
                    message
                    data {
                        fileUrl
                        _id
                    }
                }
            }
            """
            
            variables = {
                "file": f"data:image/{image_type};base64,{image_base64}",
                "filename": filename
            }
            
            result = self.client.execute_query(mutation, variables)
            
            if result:
                upload_result = result.get('data', {}).get('uploadFile', {})
                if upload_result.get('success'):
                    file_url = upload_result.get('data', {}).get('fileUrl')
                    print(f"✅ تم رفع الصورة بنجاح: {file_url}")
                    return file_url
                else:
                    print(f"❌ فشل رفع الصورة: {upload_result.get('message')}")
                    return None
            else:
                print("❌ لا توجد نتيجة من الخادم")
                return None
                
        except Exception as e:
            print(f"❌ خطأ في رفع الصورة: {e}")
            import traceback
            traceback.print_exc()
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
    # ✅ إنشاء منتج (بدون بيانات - ثم تحديث)
    # ============================================================
    def create_product(self, product_data: dict = None) -> dict:
        """إنشاء منتج جديد في قمرة (بدون بيانات)"""
        mutation = """
        mutation {
            createProduct {
                _id
                title
                slug
                status
            }
        }
        """
        
        result = self.client.execute_query(mutation, {})
        
        if result:
            data = result.get('data', {}).get('createProduct', {})
            if data:
                qid = data.get('_id') or data.get('qid')
                return {
                    'success': True,
                    'qid': qid,
                    'message': 'تم إنشاء المنتج بنجاح',
                    'data': data
                }
        
        return {
            'success': False,
            'message': 'فشل إنشاء المنتج',
            'qid': None
        }

    # ============================================================
    # ✅ تحديث معلومات المنتج
    # ============================================================
    def update_product_info(self, qid: str, title: str, description: str = "", status: str = "DRAFT"):
        """تحديث معلومات المنتج"""
        mutation = """
        mutation($id: String!, $info: UpdateProductInfo!) {
            updateProductInfo(id: $id, updateProductInfoInput: $info) {
                success
                message
            }
        }
        """
        
        variables = {
            "id": qid,
            "info": {
                "title": title,
                "description": description,
                "status": status
            }
        }
        
        result = self.client.execute_query(mutation, variables)
        
        if result:
            update_result = result.get('data', {}).get('updateProductInfo', {})
            return update_result.get('success', False)
        return False

    # ============================================================
    # ✅ تحديث سعر المنتج
    # ============================================================
    def update_product_pricing(self, qid: str, price: float):
        """تحديث سعر المنتج"""
        mutation = """
        mutation($id: ID!, $pricing: PricingInput!) {
            updateProductPricing(id: $id, pricing: $pricing) {
                success
                message
            }
        }
        """
        
        variables = {
            "id": qid,
            "pricing": {"price": price}
        }
        
        result = self.client.execute_query(mutation, variables)
        
        if result:
            update_result = result.get('data', {}).get('updateProductPricing', {})
            return update_result.get('success', False)
        return False

    # ============================================================
    # ✅ تحديث صور المنتج
    # ============================================================
    def update_product_images(self, qid: str, images: list):
        """تحديث صور المنتج"""
        mutation = """
        mutation($id: ID!, $images: [String!]!) {
            updateProductImages(id: $id, data: $images) {
                success
                message
            }
        }
        """
        
        variables = {
            "id": qid,
            "images": images
        }
        
        result = self.client.execute_query(mutation, variables)
        
        if result:
            update_result = result.get('data', {}).get('updateProductImages', {})
            return update_result.get('success', False)
        return False

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
    # ✅ تحديث بيانات المنتج (شامل)
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
