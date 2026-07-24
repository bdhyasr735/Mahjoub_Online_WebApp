# coding: utf-8
# 📂 apps/services/product_sync_service.py

"""
الخدمة الأساسية لمزامنة المنتجات مع قمرة
"""

import requests
import os
import base64
import traceback
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from apps.services.graphql_client import QomrahGraphQLClient
from apps.services.product_mapping_service import product_mapping

logger = logging.getLogger(__name__)


# ============================================================
# 🚀 MAIN SERVICE - الخدمة الأساسية
# ============================================================

class ProductSyncService:
    """
    خدمة مزامنة المنتجات مع قمرة
    تحتوي على جميع عمليات الجلب، الإنشاء، التحديث، والحذف
    """
    
    def __init__(self):
        self.client = QomrahGraphQLClient()
        self.base_url = self.client.get_base_url()

    # ============================================================
    # 🖼️ IMAGE UPLOAD - رفع الصور
    # ============================================================

    def upload_image(self, image_data: bytes, filename: str, image_type: str = None) -> Optional[str]:
        """رفع صورة إلى مكتبة قمرة"""
        try:
            if not image_type:
                image_type = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpeg'
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            mutation = """
            mutation UploadFile($file: String!, $filename: String!) {
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
                upload_result = result.get('uploadFile', {})
                if upload_result.get('success'):
                    return upload_result.get('data', {}).get('fileUrl')
            return None
                
        except Exception as e:
            logger.error(f"❌ خطأ في رفع الصورة: {e}")
            return None

    # ============================================================
    # 📦 FETCH PRODUCTS - جلب المنتجات
    # ============================================================

    def fetch_products(self, page: int = 1, limit: int = 50, title: str = "", 
                       status: str = None, collection_qid: str = None) -> Dict:
        """جلب قائمة المنتجات من قمرة"""
        query = """
        query FindAllProducts($page: Int!, $limit: Int!, $title: String, $status: String, $collectionQid: String) {
            findAllProducts(page: $page, limit: $limit, title: $title, status: $status, collectionQid: $collectionQid) {
                id
                qid
                title
                slug
                description
                status
                quantity
                price
                compareAtPrice
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
                    qid
                    quantity
                    price
                    compareAtPrice
                }
                options {
                    qid
                    name
                    values
                }
                seo {
                    title
                    description
                    keywords
                }
                createdAt
                updatedAt
            }
        }
        """
        variables = {"page": page, "limit": limit}
        if title:
            variables["title"] = title
        if status:
            variables["status"] = status
        if collection_qid:
            variables["collectionQid"] = collection_qid

        result = self.client.execute_query(query, variables)
        
        if result:
            data = result.get('findAllProducts', [])
            return {
                "data": data,
                "pagination": {
                    "currentPage": page,
                    "limit": limit,
                    "totalPages": self._calculate_total_pages(len(data), limit),
                    "total": len(data)
                }
            }
        return {"data": [], "pagination": None}

    def fetch_product_by_qid(self, qid: str) -> Optional[Dict]:
        """جلب منتج محدد من قمرة بواسطة QID"""
        query = """
        query FindProductByQid($qid: String!) {
            findProductByQid(qid: $qid) {
                id
                qid
                title
                slug
                description
                status
                quantity
                price
                compareAtPrice
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
                    qid
                    quantity
                    price
                    compareAtPrice
                }
                options {
                    qid
                    name
                    values
                }
                seo {
                    title
                    description
                    keywords
                }
                weight
                dimensions {
                    length
                    width
                    height
                }
                identification {
                    sku
                    barcode
                    barcodeType
                    hsCode
                    countryOfOrigin
                }
                createdAt
                updatedAt
            }
        }
        """
        result = self.client.execute_query(query, {"qid": qid})
        return result.get('findProductByQid') if result else None

    # ============================================================
    # ✏️ CREATE PRODUCT - إنشاء منتج
    # ============================================================

    def create_product(self, title: str, description: str = "", 
                       price: float = 0.0, status: str = "DRAFT",
                       images: List[str] = None, supplier_id: int = None,
                       **kwargs) -> Dict:
        """إنشاء منتج جديد في قمرة مع ربطه بالمورد (اختياري)"""
        try:
            mutation = """
            mutation CreateProduct($input: CreateProductInput!) {
                createProduct(input: $input) {
                    id
                    qid
                    title
                    slug
                    price
                    status
                    description
                    createdAt
                }
            }
            """
            
            input_data = {
                "title": title,
                "description": description,
                "price": price,
                "status": status
            }
            
            if images:
                input_data["images"] = images
            if kwargs.get('weight'):
                input_data["weight"] = kwargs.get('weight')
            if kwargs.get('dimensions'):
                input_data["dimensions"] = kwargs.get('dimensions')
            if kwargs.get('seo'):
                input_data["seo"] = kwargs.get('seo')
            if kwargs.get('quantity'):
                input_data["quantity"] = kwargs.get('quantity')
            if kwargs.get('sku'):
                input_data["sku"] = kwargs.get('sku')
            
            logger.info(f"🔄 جاري إنشاء المنتج: {title}")
            result = self.client.execute_query(mutation, {"input": input_data})
            
            if result:
                data = result.get('createProduct', {})
                if data:
                    qid = data.get('qid')
                    logger.info(f"✅ تم إنشاء المنتج بنجاح بـ QID: {qid}")
                    
                    if supplier_id:
                        product_mapping.add_mapping(
                            product_qid=qid,
                            supplier_id=supplier_id,
                            status='active',
                            internal_notes=f"تم إنشاء المنتج تلقائياً في {datetime.now().isoformat()}"
                        )
                    
                    return {
                        'success': True,
                        'qid': qid,
                        'message': 'تم إنشاء المنتج بنجاح',
                        'data': data
                    }
            
            return {'success': False, 'message': 'فشل إنشاء المنتج', 'qid': None, 'data': None}
                
        except Exception as e:
            logger.error(f"❌ خطأ في create_product: {e}")
            return {'success': False, 'message': f'خطأ: {str(e)}', 'qid': None, 'data': None}

    # ============================================================
    # ✏️ UPDATE PRODUCT - تحديث المنتج
    # ============================================================

    def update_product_info(self, qid: str, title: str = None, 
                            description: str = None, status: str = None) -> bool:
        """تحديث معلومات المنتج الأساسية"""
        try:
            input_data = {}
            if title is not None:
                input_data["title"] = title
            if description is not None:
                input_data["description"] = description
            if status is not None:
                input_data["status"] = status
            
            if not input_data:
                return False
            
            query = """
            mutation UpdateProductInfo($qid: String!, $input: UpdateProductInfoInput!) {
                updateProductInfo(qid: $qid, input: $input) {
                    id
                    qid
                    title
                    description
                    status
                    updatedAt
                }
            }
            """
            
            result = self.client.execute_query(query, {"qid": qid, "input": input_data})
            return bool(result and result.get('updateProductInfo'))
                
        except Exception as e:
            logger.error(f"❌ خطأ في update_product_info: {e}")
            return False

    def update_product_pricing(self, qid: str, price: float, 
                                compare_at_price: float = None) -> bool:
        """تحديث سعر المنتج"""
        try:
            query = """
            mutation UpdateProductPricing($qid: String!, $price: Float!, $compareAtPrice: Float) {
                updateProductPricing(qid: $qid, price: $price, compareAtPrice: $compareAtPrice) {
                    id
                    qid
                    price
                    compareAtPrice
                    updatedAt
                }
            }
            """
            
            variables = {"qid": qid, "price": price}
            if compare_at_price is not None:
                variables["compareAtPrice"] = compare_at_price
            
            result = self.client.execute_query(query, variables)
            return bool(result and result.get('updateProductPricing'))
                
        except Exception as e:
            logger.error(f"❌ خطأ في update_product_pricing: {e}")
            return False

    def update_product_status(self, qid: str, status: str) -> bool:
        """تحديث حالة المنتج"""
        try:
            query = """
            mutation UpdateProductStatus($qid: String!, $status: String!) {
                updateProductStatus(qid: $qid, status: $status) {
                    id
                    qid
                    status
                    updatedAt
                }
            }
            """
            
            result = self.client.execute_query(query, {"qid": qid, "status": status})
            return bool(result and result.get('updateProductStatus'))
                
        except Exception as e:
            logger.error(f"❌ خطأ في update_product_status: {e}")
            return False

    def update_product_images(self, qid: str, images: List[str]) -> bool:
        """تحديث صور المنتج (استبدال كامل)"""
        try:
            query = """
            mutation UpdateProductImages($qid: String!, $images: [String!]!) {
                updateProductImages(qid: $qid, images: $images) {
                    id
                    qid
                    images
                    updatedAt
                }
            }
            """
            
            result = self.client.execute_query(query, {"qid": qid, "images": images})
            return bool(result and result.get('updateProductImages'))
                
        except Exception as e:
            logger.error(f"❌ خطأ في update_product_images: {e}")
            return False

    def update_product_weight(self, qid: str, weight: float, unit: str = 'kg') -> bool:
        """تحديث وزن المنتج"""
        try:
            query = """
            mutation UpdateProductWeight($qid: String!, $weight: Float!, $unit: String!) {
                updateProductWeight(qid: $qid, weight: $weight, unit: $unit) {
                    id
                    qid
                    weight
                    unit
                    updatedAt
                }
            }
            """
            
            result = self.client.execute_query(query, {"qid": qid, "weight": weight, "unit": unit})
            return bool(result and result.get('updateProductWeight'))
                
        except Exception as e:
            logger.error(f"❌ خطأ في update_product_weight: {e}")
            return False

    # ============================================================
    # 🗑️ DELETE PRODUCT - حذف المنتج
    # ============================================================

    def delete_product(self, qid: str, delete_mapping: bool = True) -> bool:
        """حذف منتج من قمرة مع خيار حذف الربط"""
        try:
            query = """
            mutation DeleteProduct($qid: String!) {
                deleteProduct(qid: $qid)
            }
            """
            
            result = self.client.execute_query(query, {"qid": qid})
            
            if result and result.get('deleteProduct') is True:
                if delete_mapping:
                    product_mapping.delete_mapping(qid)
                return True
            return False
                
        except Exception as e:
            logger.error(f"❌ خطأ في delete_product: {e}")
            return False

    # ============================================================
    # 🔍 HELPER METHODS - دوال مساعدة
    # ============================================================

    def _calculate_total_pages(self, count: int, limit: int) -> int:
        """حساب عدد الصفحات"""
        return (count + limit - 1) // limit if count > 0 else 1


# ============================================================
# 🚀 INSTANCE
# ============================================================

product_sync = ProductSyncService()
