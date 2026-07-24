# coding: utf-8
# 📂 apps/services/graphql_client.py

import requests
import os
import logging
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Any, Optional, List, Union

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ✅ للتحقق من وجود المفتاح عند بدء التشغيل
print(f"🔍 QUMRA_API_KEY exists: {bool(os.environ.get('QUMRA_API_KEY'))}")
print(f"🔍 GRAPHQL_ENDPOINT: {os.environ.get('GRAPHQL_ENDPOINT', 'NOT SET')}")

_session = requests.Session()
_retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST"]
)
_adapter = HTTPAdapter(max_retries=_retry_strategy)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)


class QomrahGraphQLClient:

    @staticmethod
    def get_base_url():
        return (
            os.environ.get('GRAPHQL_ENDPOINT') or 
            os.environ.get('QUMRA_API_URL') or 
            'https://mahjoub.online/admin/graphql'
        )

    @staticmethod
    def _get_headers():
        """إعداد الـ Headers للطلب"""
        api_key = (
            os.environ.get('QUMRA_API_KEY') or 
            os.environ.get('ADMIN_JWT_TOKEN')
        )
        if not api_key:
            logging.error("❌ مفتاح API (QUMRA_API_KEY) مفقود في متغيرات البيئة.")
            return None
        
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Qomrah-Sync-Engine/1.0)"
        }

    @staticmethod
    def execute_query(query: str, variables: Optional[Dict] = None) -> Optional[Dict]:
        """
        تنفيذ أي استعلام GraphQL
        
        Args:
            query: نص الاستعلام
            variables: المتغيرات (اختياري)
        
        Returns:
            Dict: البيانات المسترجعة أو None في حالة الخطأ
        """
        print(f"🔍 Executing GraphQL query to: {QomrahGraphQLClient.get_base_url()}")
        
        headers = QomrahGraphQLClient._get_headers()
        if not headers:
            return None

        target_url = QomrahGraphQLClient.get_base_url()

        try:
            print(f"🔄 Sending request with query length: {len(query)} characters")
            response = _session.post(
                target_url,
                json={'query': query, 'variables': variables or {}},
                headers=headers,
                verify=False,
                timeout=30
            )

            print(f"📡 Response Status: {response.status_code}")
            
            if response.status_code != 200:
                logging.error(f"❌ GraphQL Status {response.status_code}: {response.text[:500]}")
                print(f"❌ HTTP Error {response.status_code}: {response.text[:500]}")
                return None

            result = response.json()

            if 'errors' in result:
                logging.error(f"❌ GraphQL Logic Error: {result['errors']}")
                print(f"❌ GraphQL Logic Error: {result['errors']}")
                return None

            print("✅ GraphQL query executed successfully")
            return result.get('data', {})

        except requests.exceptions.Timeout:
            logging.error("❌ طلب GraphQL انتهى وقته (Timeout)")
            print("❌ GraphQL Request Timeout")
            return None
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"❌ خطأ في الاتصال: {str(conn_err)}")
            print(f"❌ Connection Error: {str(conn_err)}")
            return None
        except requests.exceptions.RequestException as req_err:
            logging.error(f"❌ خطأ في الشبكة أثناء الاتصال: {str(req_err)}")
            print(f"❌ Request Exception: {str(req_err)}")
            return None
        except Exception as e:
            logging.error(f"❌ خطأ غير متوقع: {str(e)}")
            print(f"❌ Unexpected Error: {str(e)}")
            return None

    # ============================================================
    # 📦 PRODUCT QUERIES - استعلامات المنتجات
    # ============================================================

    @staticmethod
    def get_all_products() -> Optional[List[Dict]]:
        """جلب جميع المنتجات"""
        query = """
        query {
            findAllProducts {
                id
                qid
                name
                price
                status
                description
                images
                createdAt
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query)
        return result.get('findAllProducts', []) if result else []

    @staticmethod
    def get_product_by_qid(qid: str) -> Optional[Dict]:
        """جلب منتج بواسطة QID"""
        query = """
        query($qid: String!) {
            findProductByQid(qid: $qid) {
                id
                qid
                name
                price
                status
                description
                images
                weight
                dimensions {
                    length
                    width
                    height
                }
                seo {
                    title
                    description
                    keywords
                }
                collections {
                    id
                    name
                }
                variants {
                    id
                    qid
                    name
                    price
                    sku
                }
                options {
                    id
                    name
                    values
                }
                createdAt
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'qid': qid})
        return result.get('findProductByQid') if result else None

    @staticmethod
    def get_product_status(qid: str) -> Optional[Dict]:
        """جلب حالة المنتج"""
        query = """
        query($qid: String!) {
            findProductStatus(qid: $qid) {
                id
                status
                publishedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'qid': qid})
        return result.get('findProductStatus') if result else None

    @staticmethod
    def get_top_viewed_products(limit: int = 10) -> Optional[List[Dict]]:
        """جلب المنتجات الأكثر مشاهدة"""
        query = """
        query($limit: Int!) {
            FindTopViewedProducts(limit: $limit) {
                id
                qid
                name
                price
                views
                images
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'limit': limit})
        return result.get('FindTopViewedProducts', []) if result else []

    # ============================================================
    # ✏️ PRODUCT MUTATIONS - تحويرات المنتجات
    # ============================================================

    @staticmethod
    def create_product(input_data: Dict) -> Optional[Dict]:
        """
        إنشاء منتج جديد
        
        Args:
            input_data: بيانات المنتج (name, price, status, description, etc.)
        """
        query = """
        mutation($input: CreateProductInput!) {
            createProduct(input: $input) {
                id
                qid
                name
                price
                status
                createdAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'input': input_data})
        return result.get('createProduct') if result else None

    @staticmethod
    def update_product_info(qid: str, input_data: Dict) -> Optional[Dict]:
        """تحديث معلومات المنتج"""
        query = """
        mutation($qid: String!, $input: UpdateProductInfoInput!) {
            updateProductInfo(qid: $qid, input: $input) {
                id
                qid
                name
                price
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'qid': qid, 'input': input_data})
        return result.get('updateProductInfo') if result else None

    @staticmethod
    def update_product_status(qid: str, status: str) -> Optional[Dict]:
        """تحديث حالة المنتج"""
        query = """
        mutation($qid: String!, $status: String!) {
            updateProductStatus(qid: $qid, status: $status) {
                id
                qid
                status
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'qid': qid, 'status': status})
        return result.get('updateProductStatus') if result else None

    @staticmethod
    def update_product_pricing(qid: str, price: float, compare_at_price: Optional[float] = None) -> Optional[Dict]:
        """تحديث تسعير المنتج"""
        query = """
        mutation($qid: String!, $price: Float!, $compareAtPrice: Float) {
            updateProductPricing(qid: $qid, price: $price, compareAtPrice: $compareAtPrice) {
                id
                qid
                price
                compareAtPrice
                updatedAt
            }
        }
        """
        variables = {'qid': qid, 'price': price}
        if compare_at_price is not None:
            variables['compareAtPrice'] = compare_at_price
        
        result = QomrahGraphQLClient.execute_query(query, variables)
        return result.get('updateProductPricing') if result else None

    @staticmethod
    def update_product_images(qid: str, images: List[str]) -> Optional[Dict]:
        """تحديث صور المنتج"""
        query = """
        mutation($qid: String!, $images: [String!]!) {
            updateProductImages(qid: $qid, images: $images) {
                id
                qid
                images
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'qid': qid, 'images': images})
        return result.get('updateProductImages') if result else None

    @staticmethod
    def update_product_seo(qid: str, seo_data: Dict) -> Optional[Dict]:
        """تحديث SEO للمنتج"""
        query = """
        mutation($qid: String!, $seo: SEOInput!) {
            updateProductSEO(qid: $qid, seo: $seo) {
                id
                qid
                seo {
                    title
                    description
                    keywords
                }
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'qid': qid, 'seo': seo_data})
        return result.get('updateProductSEO') if result else None

    @staticmethod
    def update_product_dimensions(qid: str, dimensions: Dict) -> Optional[Dict]:
        """تحديث أبعاد المنتج"""
        query = """
        mutation($qid: String!, $dimensions: DimensionsInput!) {
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
        result = QomrahGraphQLClient.execute_query(query, {'qid': qid, 'dimensions': dimensions})
        return result.get('updateProductDimensions') if result else None

    @staticmethod
    def update_product_weight(qid: str, weight: float) -> Optional[Dict]:
        """تحديث وزن المنتج"""
        query = """
        mutation($qid: String!, $weight: Float!) {
            updateProductWeight(qid: $qid, weight: $weight) {
                id
                qid
                weight
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'qid': qid, 'weight': weight})
        return result.get('updateProductWeight') if result else None

    @staticmethod
    def update_product_description(qid: str, description: str) -> Optional[Dict]:
        """تحديث وصف المنتج"""
        query = """
        mutation($qid: String!, $description: String!) {
            updateProductDescription(qid: $qid, description: $description) {
                id
                qid
                description
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'qid': qid, 'description': description})
        return result.get('updateProductDescription') if result else None

    @staticmethod
    def update_product_collection(qid: str, collection_qids: List[str]) -> Optional[Dict]:
        """تحديث مجموعات المنتج"""
        query = """
        mutation($qid: String!, $collectionQids: [String!]!) {
            updateProductCollection(qid: $qid, collectionQids: $collectionQids) {
                id
                qid
                collections {
                    id
                    name
                }
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'qid': qid, 'collectionQids': collection_qids})
        return result.get('updateProductCollection') if result else None

    @staticmethod
    def delete_product(qid: str) -> bool:
        """حذف منتج"""
        query = """
        mutation($qid: String!) {
            deleteProduct(qid: $qid)
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'qid': qid})
        return result.get('deleteProduct', False) if result else False

    @staticmethod
    def bulk_delete_products(qids: List[str]) -> bool:
        """حذف منتجات متعددة"""
        query = """
        mutation($qids: [String!]!) {
            bulkDeleteProduct(qids: $qids)
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'qids': qids})
        return result.get('bulkDeleteProduct', False) if result else False

    @staticmethod
    def bulk_update_products_status(qids: List[str], status: str) -> Optional[List[Dict]]:
        """تحديث حالة منتجات متعددة"""
        query = """
        mutation($qids: [String!]!, $status: String!) {
            bulkUpdateProductsStatus(qids: $qids, status: $status) {
                id
                qid
                status
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'qids': qids, 'status': status})
        return result.get('bulkUpdateProductsStatus', []) if result else []

    # ============================================================
    # 🎨 VARIANT QUERIES & MUTATIONS
    # ============================================================

    @staticmethod
    def get_variants_by_product(product_qid: str) -> Optional[List[Dict]]:
        """جلب جميع الفاريانتات لمنتج"""
        query = """
        query($productQid: String!) {
            findAllVariantsByProductId(productQid: $productQid) {
                id
                qid
                name
                price
                sku
                stock
                media
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'productQid': product_qid})
        return result.get('findAllVariantsByProductId', []) if result else []

    @staticmethod
    def get_variant_by_id(variant_qid: str) -> Optional[Dict]:
        """جلب فاريانت بواسطة QID"""
        query = """
        query($variantQid: String!) {
            findVariantById(variantQid: $variantQid) {
                id
                qid
                name
                price
                sku
                stock
                media
                createdAt
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'variantQid': variant_qid})
        return result.get('findVariantById') if result else None

    @staticmethod
    def update_variant_pricing(variant_qid: str, price: float) -> Optional[Dict]:
        """تحديث تسعير فاريانت"""
        query = """
        mutation($variantQid: String!, $price: Float!) {
            updateVariantPricing(variantQid: $variantQid, price: $price) {
                id
                qid
                price
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'variantQid': variant_qid, 'price': price})
        return result.get('updateVariantPricing') if result else None

    @staticmethod
    def update_variant_media(variant_qid: str, media: List[str]) -> Optional[Dict]:
        """تحديث وسائط الفاريانت"""
        query = """
        mutation($variantQid: String!, $media: [String!]!) {
            updateVariantMedia(variantQid: $variantQid, media: $media) {
                id
                qid
                media
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'variantQid': variant_qid, 'media': media})
        return result.get('updateVariantMedia') if result else None

    @staticmethod
    def remove_variant(variant_qid: str) -> bool:
        """حذف فاريانت"""
        query = """
        mutation($variantQid: String!) {
            removeVariantById(variantQid: $variantQid)
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'variantQid': variant_qid})
        return result.get('removeVariantById', False) if result else False

    @staticmethod
    def bulk_variant_update(variants: List[Dict]) -> Optional[List[Dict]]:
        """تحديث فاريانتات متعددة دفعة واحدة"""
        query = """
        mutation($variants: [VariantUpdateInput!]!) {
            bulkVariantUpdate(variants: $variants) {
                id
                qid
                name
                price
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'variants': variants})
        return result.get('bulkVariantUpdate', []) if result else []

    # ============================================================
    # 🎯 OPTION QUERIES & MUTATIONS
    # ============================================================

    @staticmethod
    def get_option_by_qid(option_qid: str) -> Optional[Dict]:
        """جلب خيار بواسطة QID"""
        query = """
        query($optionQid: String!) {
            findOptionByQid(optionQid: $optionQid) {
                id
                qid
                name
                values
                productId
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'optionQid': option_qid})
        return result.get('findOptionByQid') if result else None

    @staticmethod
    def get_options_for_product(product_qid: str) -> Optional[List[Dict]]:
        """جلب جميع خيارات المنتج"""
        query = """
        query($productQid: String!) {
            findAllOptionsForProduct(productQid: $productQid) {
                id
                qid
                name
                values
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'productQid': product_qid})
        return result.get('findAllOptionsForProduct', []) if result else []

    @staticmethod
    def create_option(input_data: Dict) -> Optional[Dict]:
        """إنشاء خيار جديد"""
        query = """
        mutation($input: CreateOptionInput!) {
            createOption(input: $input) {
                id
                qid
                name
                values
                createdAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'input': input_data})
        return result.get('createOption') if result else None

    @staticmethod
    def update_option(option_qid: str, input_data: Dict) -> Optional[Dict]:
        """تحديث خيار"""
        query = """
        mutation($optionQid: String!, $input: UpdateOptionInput!) {
            updateOption(optionQid: $optionQid, input: $input) {
                id
                qid
                name
                values
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'optionQid': option_qid, 'input': input_data})
        return result.get('updateOption') if result else None

    @staticmethod
    def remove_option(option_qid: str) -> bool:
        """حذف خيار"""
        query = """
        mutation($optionQid: String!) {
            removeOption(optionQid: $optionQid)
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'optionQid': option_qid})
        return result.get('removeOption', False) if result else False

    # ============================================================
    # 📂 COLLECTION QUERIES & MUTATIONS
    # ============================================================

    @staticmethod
    def get_all_collections() -> Optional[List[Dict]]:
        """جلب جميع المجموعات"""
        query = """
        query {
            findAllCollections {
                id
                qid
                name
                description
                image
                productsCount
                createdAt
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query)
        return result.get('findAllCollections', []) if result else []

    @staticmethod
    def get_collection_by_qid(qid: str) -> Optional[Dict]:
        """جلب مجموعة بواسطة QID"""
        query = """
        query($qid: String!) {
            findCollectionByQid(qid: $qid) {
                id
                qid
                name
                description
                image
                products {
                    id
                    qid
                    name
                    price
                }
                createdAt
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'qid': qid})
        return result.get('findCollectionByQid') if result else None

    @staticmethod
    def get_products_for_collection(collection_qid: str) -> Optional[List[Dict]]:
        """جلب منتجات مجموعة معينة"""
        query = """
        query($collectionQid: String!) {
            findAllProductsForCollection(collectionQid: $collectionQid) {
                id
                qid
                name
                price
                status
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'collectionQid': collection_qid})
        return result.get('findAllProductsForCollection', []) if result else []

    @staticmethod
    def create_collection(input_data: Dict) -> Optional[Dict]:
        """إنشاء مجموعة جديدة"""
        query = """
        mutation($input: CreateCollectionInput!) {
            createCollection(input: $input) {
                id
                qid
                name
                description
                createdAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'input': input_data})
        return result.get('createCollection') if result else None

    @staticmethod
    def update_collection(qid: str, input_data: Dict) -> Optional[Dict]:
        """تحديث مجموعة"""
        query = """
        mutation($qid: String!, $input: UpdateCollectionInput!) {
            updateCollection(qid: $qid, input: $input) {
                id
                qid
                name
                description
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'qid': qid, 'input': input_data})
        return result.get('updateCollection') if result else None

    @staticmethod
    def remove_collection(qid: str) -> bool:
        """حذف مجموعة"""
        query = """
        mutation($qid: String!) {
            removeCollection(qid: $qid)
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'qid': qid})
        return result.get('removeCollection', False) if result else False

    @staticmethod
    def add_product_to_collections(product_qid: str, collection_qids: List[str]) -> Optional[Dict]:
        """إضافة منتج لمجموعات"""
        query = """
        mutation($productQid: String!, $collectionQids: [String!]!) {
            AddProductToCollections(productQid: $productQid, collectionQids: $collectionQids) {
                id
                qid
                collections {
                    id
                    name
                }
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'productQid': product_qid, 'collectionQids': collection_qids})
        return result.get('AddProductToCollections') if result else None

    # ============================================================
    # 📦 ORDER QUERIES & MUTATIONS
    # ============================================================

    @staticmethod
    def get_all_orders() -> Optional[List[Dict]]:
        """جلب جميع الطلبات"""
        query = """
        query {
            findAllOrders {
                id
                qid
                orderNumber
                total
                status
                currency
                customer {
                    id
                    name
                    email
                    phone
                }
                shipping {
                    address
                    city
                    country
                    method
                }
                items {
                    id
                    productId
                    productName
                    quantity
                    price
                }
                createdAt
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query)
        return result.get('findAllOrders', []) if result else []

    @staticmethod
    def get_orders_by_ids(order_ids: List[str]) -> Optional[List[Dict]]:
        """جلب طلبات بواسطة معرفاتها"""
        query = """
        query($orderIds: [String!]!) {
            getOrdersByIds(orderIds: $orderIds) {
                id
                qid
                orderNumber
                total
                status
                customer {
                    name
                    email
                }
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'orderIds': order_ids})
        return result.get('getOrdersByIds', []) if result else []

    @staticmethod
    def get_order_by_id(order_id: str) -> Optional[Dict]:
        """جلب طلب بواسطة معرفه"""
        query = """
        query($orderId: String!) {
            findOrderById(orderId: $orderId) {
                id
                qid
                orderNumber
                total
                status
                currency
                customer {
                    id
                    name
                    email
                    phone
                }
                shipping {
                    address
                    city
                    country
                    method
                    trackingNumber
                }
                items {
                    id
                    productId
                    productName
                    quantity
                    price
                    total
                }
                payment {
                    method
                    status
                    transactionId
                }
                timeline {
                    id
                    event
                    description
                    createdAt
                }
                createdAt
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'orderId': order_id})
        return result.get('findOrderById') if result else None

    @staticmethod
    def get_order_status(order_id: str) -> Optional[Dict]:
        """جلب حالة الطلب"""
        query = """
        query($orderId: String!) {
            findOrderStatus(orderId: $orderId) {
                id
                status
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'orderId': order_id})
        return result.get('findOrderStatus') if result else None

    @staticmethod
    def get_order_timeline(order_id: str) -> Optional[List[Dict]]:
        """جلب الجدول الزمني للطلب"""
        query = """
        query($orderId: String!) {
            findOrderTimeline(orderId: $orderId) {
                id
                event
                description
                createdAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'orderId': order_id})
        return result.get('findOrderTimeline', []) if result else []

    @staticmethod
    def get_order_statistics() -> Optional[Dict]:
        """جلب إحصائيات الطلبات"""
        query = """
        query {
            orderStatistics {
                totalOrders
                totalRevenue
                averageOrderValue
                ordersByStatus {
                    status
                    count
                    total
                }
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query)
        return result.get('orderStatistics') if result else {}

    @staticmethod
    def get_total_revenue(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Optional[Dict]:
        """جلب إجمالي الإيرادات"""
        query = """
        query($startDate: String, $endDate: String) {
            totalRevenue(startDate: $startDate, endDate: $endDate) {
                total
                currency
                period
            }
        }
        """
        variables = {}
        if start_date:
            variables['startDate'] = start_date
        if end_date:
            variables['endDate'] = end_date
        
        result = QomrahGraphQLClient.execute_query(query, variables)
        return result.get('totalRevenue') if result else {}

    @staticmethod
    def get_order_settings() -> Optional[Dict]:
        """جلب إعدادات الطلبات"""
        query = """
        query {
            orderSettings {
                id
                autoConfirm
                paymentMethods
                shippingMethods
                taxSettings
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query)
        return result.get('orderSettings') if result else {}

    @staticmethod
    def change_order_status(order_id: str, status: str) -> Optional[Dict]:
        """تغيير حالة الطلب"""
        query = """
        mutation($orderId: String!, $status: String!) {
            changeOrderStatus(orderId: $orderId, status: $status) {
                id
                qid
                status
                updatedAt
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'orderId': order_id, 'status': status})
        return result.get('changeOrderStatus') if result else None

    @staticmethod
    def update_order_payment(order_id: str, payment_data: Dict) -> Optional[Dict]:
        """تحديث حالة الدفع للطلب"""
        query = """
        mutation($orderId: String!, $payment: PaymentInput!) {
            updateOrderPayment(orderId: $orderId, payment: $payment) {
                id
                qid
                payment {
                    status
                    method
                    updatedAt
                }
            }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, {'orderId': order_id, 'payment': payment_data})
        return result.get('updateOrderPayment') if result else None
