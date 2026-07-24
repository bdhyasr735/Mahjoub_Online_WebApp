# coding: utf-8
# 📂 apps/services/product_sync_service.py

from apps.services.graphql_client import QomrahGraphQLClient
import requests
import os
import base64
import traceback
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


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
        """
        رفع صورة إلى مكتبة قمرة باستخدام GraphQL Mutation مع base64
        
        Args:
            image_data: بيانات الصورة (bytes)
            filename: اسم الملف
            image_type: نوع الصورة (jpeg, png, gif) - يتم استخراجه من الاسم إن لم يُقدم
        
        Returns:
            str: رابط الصورة المرفوعة أو None في حالة الفشل
        """
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
                        file
                        path
                        mimetype
                        sizeInKB
                        sizeInMB
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
                    file_url = upload_result.get('data', {}).get('fileUrl')
                    file_id = upload_result.get('data', {}).get('_id')
                    print(f"✅ تم رفع الصورة بنجاح: {file_url}")
                    print(f"   📎 ID: {file_id}")
                    return file_url
                else:
                    print(f"❌ فشل رفع الصورة: {upload_result.get('message')}")
                    return None
            else:
                print("❌ لا توجد نتيجة من الخادم")
                return None
                
        except Exception as e:
            print(f"❌ خطأ في رفع الصورة: {e}")
            traceback.print_exc()
            return None

    def upload_multiple_images(self, images: List[Tuple[bytes, str]]) -> List[str]:
        """
        رفع عدة صور دفعة واحدة
        
        Args:
            images: قائمة من (image_data, filename)
        
        Returns:
            List[str]: قائمة روابط الصور المرفوعة
        """
        uploaded_urls = []
        for image_data, filename in images:
            url = self.upload_image(image_data, filename)
            if url:
                uploaded_urls.append(url)
        return uploaded_urls

    # ============================================================
    # 📦 FETCH PRODUCTS - جلب المنتجات
    # ============================================================

    def fetch_products(self, page: int = 1, limit: int = 50, title: str = "", 
                       status: str = None, collection_qid: str = None) -> Dict:
        """
        جلب قائمة المنتجات من قمرة
        
        Args:
            page: رقم الصفحة
            limit: عدد المنتجات في الصفحة
            title: فلترة حسب الاسم (اختياري)
            status: فلترة حسب الحالة (اختياري)
            collection_qid: فلترة حسب المجموعة (اختياري)
        
        Returns:
            Dict: {data: List[Dict], pagination: Dict}
        """
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

    def fetch_all_products_paginated(self, limit: int = 50, **filters) -> List[Dict]:
        """
        جلب جميع المنتجات عبر الصفحات
        
        Args:
            limit: عدد المنتجات في الصفحة
            **filters: أي فلتر إضافي (title, status, collection_qid)
        
        Returns:
            List[Dict]: قائمة بجميع المنتجات
        """
        all_products = []
        page = 1
        
        while True:
            result = self.fetch_products(page=page, limit=limit, **filters)
            products = result.get('data', [])
            
            if not products:
                break
                
            all_products.extend(products)
            page += 1
            
            # توقف إذا وصلنا لآخر صفحة
            pagination = result.get('pagination', {})
            if pagination and pagination.get('totalPages', 0) < page:
                break
        
        print(f"✅ تم جلب {len(all_products)} منتج")
        return all_products

    def fetch_product_by_qid(self, qid: str) -> Optional[Dict]:
        """
        جلب منتج محدد من قمرة بواسطة QID
        
        Args:
            qid: معرف المنتج
        
        Returns:
            Dict: بيانات المنتج أو None
        """
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

    def fetch_product_status(self, qid: str) -> Optional[Dict]:
        """
        جلب حالة المنتج
        
        Args:
            qid: معرف المنتج
        
        Returns:
            Dict: {id, status, publishedAt}
        """
        query = """
        query FindProductStatus($qid: String!) {
            findProductStatus(qid: $qid) {
                id
                status
                publishedAt
            }
        }
        """
        result = self.client.execute_query(query, {"qid": qid})
        return result.get('findProductStatus') if result else None

    def fetch_top_viewed_products(self, limit: int = 10) -> List[Dict]:
        """
        جلب المنتجات الأكثر مشاهدة
        
        Args:
            limit: عدد المنتجات
        
        Returns:
            List[Dict]: قائمة المنتجات
        """
        query = """
        query FindTopViewedProducts($limit: Int!) {
            FindTopViewedProducts(limit: $limit) {
                id
                qid
                title
                price
                views
                images {
                    fileUrl
                }
            }
        }
        """
        result = self.client.execute_query(query, {"limit": limit})
        return result.get('FindTopViewedProducts', []) if result else []

    # ============================================================
    # 📂 FETCH COLLECTIONS - جلب المجموعات
    # ============================================================

    def fetch_collections(self, page: int = 1, limit: int = 100) -> List[Dict]:
        """
        جلب قائمة المجموعات من قمرة
        
        Args:
            page: رقم الصفحة
            limit: عدد المجموعات في الصفحة
        
        Returns:
            List[Dict]: قائمة المجموعات
        """
        query = """
        query FindAllCollections($page: Int!, $limit: Int!) {
            findAllCollections(page: $page, limit: $limit) {
                id
                qid
                title
                slug
                description
                image {
                    fileUrl
                }
                productCount
                createdAt
                updatedAt
            }
        }
        """
        result = self.client.execute_query(query, {"page": page, "limit": limit})
        return result.get('findAllCollections', []) if result else []

    def fetch_collection_by_qid(self, qid: str) -> Optional[Dict]:
        """
        جلب مجموعة بواسطة QID
        
        Args:
            qid: معرف المجموعة
        
        Returns:
            Dict: بيانات المجموعة
        """
        query = """
        query FindCollectionByQid($qid: String!) {
            findCollectionByQid(qid: $qid) {
                id
                qid
                title
                slug
                description
                image {
                    fileUrl
                }
                products {
                    id
                    qid
                    title
                    price
                }
                productCount
                createdAt
                updatedAt
            }
        }
        """
        result = self.client.execute_query(query, {"qid": qid})
        return result.get('findCollectionByQid') if result else None

    # ============================================================
    # ✏️ CREATE PRODUCT - إنشاء منتج
    # ============================================================

    def create_product(self, title: str, description: str = "", 
                       price: float = 0.0, status: str = "DRAFT",
                       images: List[str] = None, **kwargs) -> Dict:
        """
        إنشاء منتج جديد في قمرة
        
        Args:
            title: اسم المنتج
            description: وصف المنتج
            price: السعر
            status: الحالة (DRAFT, ACTIVE, INACTIVE, ARCHIVED)
            images: قائمة روابط الصور
            **kwargs: حقول إضافية (weight, dimensions, seo, etc.)
        
        Returns:
            Dict: {success: bool, qid: str, message: str, data: dict}
        """
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
            
            print(f"🔄 جاري إنشاء المنتج: {title}")
            result = self.client.execute_query(mutation, {"input": input_data})
            
            if result:
                data = result.get('createProduct', {})
                if data:
                    qid = data.get('qid')
                    print(f"✅ تم إنشاء المنتج بنجاح بـ QID: {qid}")
                    return {
                        'success': True,
                        'qid': qid,
                        'message': 'تم إنشاء المنتج بنجاح',
                        'data': data
                    }
            
            print(f"❌ فشل إنشاء المنتج")
            return {
                'success': False,
                'message': 'فشل إنشاء المنتج',
                'qid': None,
                'data': None
            }
                
        except Exception as e:
            print(f"❌ خطأ في create_product: {e}")
            traceback.print_exc()
            return {
                'success': False,
                'message': f'خطأ: {str(e)}',
                'qid': None,
                'data': None
            }

    # ============================================================
    # ✏️ UPDATE PRODUCT - تحديث المنتج
    # ============================================================

    def update_product_info(self, qid: str, title: str = None, 
                            description: str = None, status: str = None) -> bool:
        """
        تحديث معلومات المنتج الأساسية
        
        Args:
            qid: معرف المنتج
            title: الاسم الجديد (اختياري)
            description: الوصف الجديد (اختياري)
            status: الحالة الجديدة (اختياري)
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        try:
            input_data = {}
            if title is not None:
                input_data["title"] = title
            if description is not None:
                input_data["description"] = description
            if status is not None:
                input_data["status"] = status
            
            if not input_data:
                print("⚠️ لا توجد بيانات للتحديث")
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
            
            print(f"🔄 جاري تحديث معلومات المنتج {qid}")
            result = self.client.execute_query(query, {"qid": qid, "input": input_data})
            
            if result and result.get('updateProductInfo'):
                print(f"✅ تم تحديث معلومات المنتج بنجاح")
                return True
            else:
                print(f"❌ فشل تحديث معلومات المنتج")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في update_product_info: {e}")
            traceback.print_exc()
            return False

    def update_product_pricing(self, qid: str, price: float, 
                                compare_at_price: float = None) -> bool:
        """
        تحديث سعر المنتج
        
        Args:
            qid: معرف المنتج
            price: السعر الجديد
            compare_at_price: السعر المقارن (اختياري)
        
        Returns:
            bool: نجاح أو فشل العملية
        """
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
            
            print(f"🔄 جاري تحديث سعر المنتج {qid}: {price}")
            result = self.client.execute_query(query, variables)
            
            if result and result.get('updateProductPricing'):
                print(f"✅ تم تحديث سعر المنتج بنجاح")
                return True
            else:
                print(f"❌ فشل تحديث سعر المنتج")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في update_product_pricing: {e}")
            traceback.print_exc()
            return False

    def update_product_status(self, qid: str, status: str) -> bool:
        """
        تحديث حالة المنتج
        
        Args:
            qid: معرف المنتج
            status: الحالة الجديدة (ACTIVE, INACTIVE, DRAFT, ARCHIVED)
        
        Returns:
            bool: نجاح أو فشل العملية
        """
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
            
            print(f"🔄 جاري تحديث حالة المنتج {qid} إلى {status}")
            result = self.client.execute_query(query, {"qid": qid, "status": status})
            
            if result and result.get('updateProductStatus'):
                print(f"✅ تم تحديث حالة المنتج إلى {status}")
                return True
            else:
                print(f"❌ فشل تحديث حالة المنتج")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في update_product_status: {e}")
            traceback.print_exc()
            return False

    def update_product_images(self, qid: str, images: List[str]) -> bool:
        """
        تحديث صور المنتج (استبدال كامل)
        
        Args:
            qid: معرف المنتج
            images: قائمة روابط الصور الجديدة
        
        Returns:
            bool: نجاح أو فشل العملية
        """
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
            
            print(f"🔄 جاري تحديث صور المنتج {qid}")
            result = self.client.execute_query(query, {"qid": qid, "images": images})
            
            if result and result.get('updateProductImages'):
                print(f"✅ تم تحديث صور المنتج بنجاح")
                return True
            else:
                print(f"❌ فشل تحديث صور المنتج")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في update_product_images: {e}")
            traceback.print_exc()
            return False

    def update_product_dimensions(self, qid: str, dimensions: Dict[str, float]) -> bool:
        """
        تحديث أبعاد المنتج
        
        Args:
            qid: معرف المنتج
            dimensions: {length, width, height, unit?}
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        try:
            query = """
            mutation UpdateProductDimensions($qid: String!, $dimensions: DimensionsInput!) {
                updateProductDimensions(qid: $qid, dimensions: $dimensions) {
                    id
                    qid
                    dimensions {
                        length
                        width
                        height
                    }
                    updatedAt
                }
            }
            """
            
            print(f"🔄 جاري تحديث أبعاد المنتج {qid}")
            result = self.client.execute_query(query, {"qid": qid, "dimensions": dimensions})
            
            if result and result.get('updateProductDimensions'):
                print(f"✅ تم تحديث أبعاد المنتج بنجاح")
                return True
            else:
                print(f"❌ فشل تحديث أبعاد المنتج")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في update_product_dimensions: {e}")
            traceback.print_exc()
            return False

    def update_product_weight(self, qid: str, weight: float, unit: str = 'kg') -> bool:
        """
        تحديث وزن المنتج
        
        Args:
            qid: معرف المنتج
            weight: الوزن
            unit: وحدة الوزن (kg, g, lb, oz)
        
        Returns:
            bool: نجاح أو فشل العملية
        """
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
            
            print(f"🔄 جاري تحديث وزن المنتج {qid}: {weight} {unit}")
            result = self.client.execute_query(query, {"qid": qid, "weight": weight, "unit": unit})
            
            if result and result.get('updateProductWeight'):
                print(f"✅ تم تحديث وزن المنتج بنجاح")
                return True
            else:
                print(f"❌ فشل تحديث وزن المنتج")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في update_product_weight: {e}")
            traceback.print_exc()
            return False

    def update_product_seo(self, qid: str, seo_data: Dict[str, str]) -> bool:
        """
        تحديث SEO للمنتج
        
        Args:
            qid: معرف المنتج
            seo_data: {title, description, keywords, image, canonicalUrl}
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        try:
            query = """
            mutation UpdateProductSEO($qid: String!, $seo: SEOInput!) {
                updateProductSEO(qid: $qid, seo: $seo) {
                    id
                    qid
                    seo {
                        title
                        description
                        keywords
                        image
                        canonicalUrl
                    }
                    updatedAt
                }
            }
            """
            
            print(f"🔄 جاري تحديث SEO للمنتج {qid}")
            result = self.client.execute_query(query, {"qid": qid, "seo": seo_data})
            
            if result and result.get('updateProductSEO'):
                print(f"✅ تم تحديث SEO للمنتج بنجاح")
                return True
            else:
                print(f"❌ فشل تحديث SEO للمنتج")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في update_product_seo: {e}")
            traceback.print_exc()
            return False

    def update_product_description(self, qid: str, description: str) -> bool:
        """
        تحديث وصف المنتج
        
        Args:
            qid: معرف المنتج
            description: النص الجديد للوصف
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        try:
            query = """
            mutation UpdateProductDescription($qid: String!, $description: String!) {
                updateProductDescription(qid: $qid, description: $description) {
                    id
                    qid
                    description
                    updatedAt
                }
            }
            """
            
            print(f"🔄 جاري تحديث وصف المنتج {qid}")
            result = self.client.execute_query(query, {"qid": qid, "description": description})
            
            if result and result.get('updateProductDescription'):
                print(f"✅ تم تحديث وصف المنتج بنجاح")
                return True
            else:
                print(f"❌ فشل تحديث وصف المنتج")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في update_product_description: {e}")
            traceback.print_exc()
            return False

    def update_product_collection(self, qid: str, collection_qids: List[str]) -> bool:
        """
        تحديث مجموعات المنتج
        
        Args:
            qid: معرف المنتج
            collection_qids: قائمة معرفات المجموعات
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        try:
            query = """
            mutation UpdateProductCollection($qid: String!, $collectionQids: [String!]!) {
                updateProductCollection(qid: $qid, collectionQids: $collectionQids) {
                    id
                    qid
                    collections {
                        id
                        qid
                        title
                    }
                    updatedAt
                }
            }
            """
            
            print(f"🔄 جاري تحديث مجموعات المنتج {qid}")
            result = self.client.execute_query(query, {"qid": qid, "collectionQids": collection_qids})
            
            if result and result.get('updateProductCollection'):
                print(f"✅ تم تحديث مجموعات المنتج بنجاح")
                return True
            else:
                print(f"❌ فشل تحديث مجموعات المنتج")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في update_product_collection: {e}")
            traceback.print_exc()
            return False

    # ============================================================
    # 🗑️ DELETE PRODUCT - حذف المنتج
    # ============================================================

    def delete_product(self, qid: str) -> bool:
        """
        حذف منتج من قمرة
        
        Args:
            qid: معرف المنتج
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        try:
            query = """
            mutation DeleteProduct($qid: String!) {
                deleteProduct(qid: $qid)
            }
            """
            
            print(f"🔄 جاري حذف المنتج {qid}")
            result = self.client.execute_query(query, {"qid": qid})
            
            if result and result.get('deleteProduct') is True:
                print(f"✅ تم حذف المنتج {qid} بنجاح")
                return True
            else:
                print(f"❌ فشل حذف المنتج")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في delete_product: {e}")
            traceback.print_exc()
            return False

    def bulk_delete_products(self, qids: List[str]) -> bool:
        """
        حذف منتجات متعددة
        
        Args:
            qids: قائمة معرفات المنتجات
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        try:
            query = """
            mutation BulkDeleteProduct($qids: [String!]!) {
                bulkDeleteProduct(qids: $qids)
            }
            """
            
            print(f"🔄 جاري حذف {len(qids)} منتج")
            result = self.client.execute_query(query, {"qids": qids})
            
            if result and result.get('bulkDeleteProduct') is True:
                print(f"✅ تم حذف {len(qids)} منتج بنجاح")
                return True
            else:
                print(f"❌ فشل حذف المنتجات")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في bulk_delete_products: {e}")
            traceback.print_exc()
            return False

    # ============================================================
    # 🎨 VARIANT OPERATIONS - عمليات الفاريانتات
    # ============================================================

    def update_variant_pricing(self, variant_qid: str, price: float, 
                                compare_at_price: float = None) -> bool:
        """
        تحديث تسعير الفاريانت
        
        Args:
            variant_qid: معرف الفاريانت
            price: السعر الجديد
            compare_at_price: السعر المقارن (اختياري)
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        try:
            query = """
            mutation UpdateVariantPricing($variantQid: String!, $price: Float!, $compareAtPrice: Float) {
                updateVariantPricing(variantQid: $variantQid, price: $price, compareAtPrice: $compareAtPrice) {
                    id
                    qid
                    price
                    compareAtPrice
                    updatedAt
                }
            }
            """
            
            variables = {"variantQid": variant_qid, "price": price}
            if compare_at_price is not None:
                variables["compareAtPrice"] = compare_at_price
            
            print(f"🔄 جاري تحديث سعر الفاريانت {variant_qid}")
            result = self.client.execute_query(query, variables)
            
            if result and result.get('updateVariantPricing'):
                print(f"✅ تم تحديث سعر الفاريانت بنجاح")
                return True
            else:
                print(f"❌ فشل تحديث سعر الفاريانت")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في update_variant_pricing: {e}")
            traceback.print_exc()
            return False

    def remove_variant(self, variant_qid: str) -> bool:
        """
        حذف فاريانت
        
        Args:
            variant_qid: معرف الفاريانت
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        try:
            query = """
            mutation RemoveVariant($variantQid: String!) {
                removeVariantById(variantQid: $variantQid)
            }
            """
            
            print(f"🔄 جاري حذف الفاريانت {variant_qid}")
            result = self.client.execute_query(query, {"variantQid": variant_qid})
            
            if result and result.get('removeVariantById') is True:
                print(f"✅ تم حذف الفاريانت بنجاح")
                return True
            else:
                print(f"❌ فشل حذف الفاريانت")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في remove_variant: {e}")
            traceback.print_exc()
            return False

    # ============================================================
    # 🔍 HELPER METHODS - دوال مساعدة
    # ============================================================

    def _calculate_total_pages(self, count: int, limit: int) -> int:
        """حساب عدد الصفحات"""
        return (count + limit - 1) // limit if count > 0 else 1

    def sync_product_complete(self, qid: str, data: Dict) -> bool:
        """
        مزامنة كاملة للمنتج (جميع الحقول)
        
        Args:
            qid: معرف المنتج
            data: جميع بيانات المنتج {title, description, price, status, ...}
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        try:
            success = True
            
            # تحديث المعلومات الأساسية
            if 'title' in data or 'description' in data or 'status' in data:
                info_data = {}
                if 'title' in data:
                    info_data['title'] = data['title']
                if 'description' in data:
                    info_data['description'] = data['description']
                if 'status' in data:
                    info_data['status'] = data['status']
                if info_data:
                    if not self.update_product_info(qid, **info_data):
                        success = False
            
            # تحديث السعر
            if 'price' in data:
                if not self.update_product_pricing(qid, data['price'], data.get('compare_at_price')):
                    success = False
            
            # تحديث الصور
            if 'images' in data:
                if not self.update_product_images(qid, data['images']):
                    success = False
            
            # تحديث الأبعاد
            if 'dimensions' in data:
                if not self.update_product_dimensions(qid, data['dimensions']):
                    success = False
            
            # تحديث الوزن
            if 'weight' in data:
                if not self.update_product_weight(qid, data['weight'], data.get('weight_unit', 'kg')):
                    success = False
            
            # تحديث SEO
            if 'seo' in data:
                if not self.update_product_seo(qid, data['seo']):
                    success = False
            
            # تحديث المجموعات
            if 'collections' in data:
                if not self.update_product_collection(qid, data['collections']):
                    success = False
            
            return success
            
        except Exception as e:
            print(f"❌ خطأ في sync_product_complete: {e}")
            traceback.print_exc()
            return False

    def get_product_stats(self) -> Dict:
        """
        الحصول على إحصائيات المنتجات
        
        Returns:
            Dict: {total, active, inactive, draft, archived}
        """
        try:
            all_products = self.fetch_all_products_paginated(limit=100)
            
            stats = {
                'total': len(all_products),
                'active': 0,
                'inactive': 0,
                'draft': 0,
                'archived': 0
            }
            
            for product in all_products:
                status = product.get('status', '').upper()
                if status == 'ACTIVE':
                    stats['active'] += 1
                elif status == 'INACTIVE':
                    stats['inactive'] += 1
                elif status == 'DRAFT':
                    stats['draft'] += 1
                elif status == 'ARCHIVED':
                    stats['archived'] += 1
            
            return stats
            
        except Exception as e:
            print(f"❌ خطأ في get_product_stats: {e}")
            return {'total': 0, 'active': 0, 'inactive': 0, 'draft': 0, 'archived': 0}


# ============================================================
# 🚀 INSTANCE
# ============================================================

product_sync = ProductSyncService()
