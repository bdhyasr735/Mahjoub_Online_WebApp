# coding: utf-8
# 📂 apps/services/fetch_product_data.graphql.py

from typing import Dict, List, Optional, Any
from .graphql_client import QomrahGraphQLClient


# ============================================================
# 📋 QUERIES - استعلامات المنتجات
# ============================================================

GET_PRODUCT_DETAIL_QUERY = """
query GetProductByQid($qid: String!) {
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
            title
            description
            mimetype
            sizeInKB
            sizeInMB
        }
        collections {
            id
            qid
            title
            slug
            description
            image {
                fileUrl
            }
            productCount
        }
        variants {
            id
            qid
            quantity
            price
            compareAtPrice
            sku
            barcode
            weight
            dimensions {
                length
                width
                height
            }
            images {
                _id
                fileUrl
            }
            options {
                qid
                option
                label
                sortOrder
            }
        }
        options {
            id
            qid
            name
            type
            values
            productId
        }
        seo {
            title
            description
            keywords
            image
            canonicalUrl
        }
        weight
        weightUnit
        dimensions {
            length
            width
            height
            unit
        }
        identification {
            sku
            barcode
            barcodeType
            hsCode
            countryOfOrigin
            mpn
        }
        tags
        views
        reviews {
            id
            rating
            comment
            customerName
            createdAt
        }
        reviewsCount
        averageRating
        createdAt
        updatedAt
        publishedAt
    }
}
"""

GET_ALL_PRODUCTS_QUERY = """
query GetAllProducts($page: Int, $limit: Int, $title: String, $status: String, $collectionQid: String) {
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
        variantsCount
        views
        createdAt
        updatedAt
    }
}
"""

GET_PRODUCT_STATUS_QUERY = """
query GetProductStatus($qid: String!) {
    findProductStatus(qid: $qid) {
        id
        status
        publishedAt
        updatedAt
    }
}
"""

GET_TOP_VIEWED_PRODUCTS_QUERY = """
query GetTopViewedProducts($limit: Int!) {
    FindTopViewedProducts(limit: $limit) {
        id
        qid
        title
        slug
        price
        views
        images {
            _id
            fileUrl
        }
        createdAt
    }
}
"""

GET_PRODUCT_VARIANTS_QUERY = """
query GetProductVariants($productQid: String!) {
    findAllVariantsByProductId(productQid: $productQid) {
        id
        qid
        name
        price
        compareAtPrice
        sku
        barcode
        quantity
        stock
        weight
        dimensions {
            length
            width
            height
        }
        images {
            _id
            fileUrl
        }
        options {
            qid
            option
            label
            sortOrder
        }
        media
        createdAt
        updatedAt
    }
}
"""

GET_VARIANT_BY_ID_QUERY = """
query GetVariantById($variantQid: String!) {
    findVariantById(variantQid: $variantQid) {
        id
        qid
        name
        price
        compareAtPrice
        sku
        barcode
        quantity
        stock
        weight
        dimensions {
            length
            width
            height
        }
        images {
            _id
            fileUrl
        }
        options {
            qid
            option
            label
            sortOrder
        }
        media
        product {
            id
            qid
            title
            slug
        }
        createdAt
        updatedAt
    }
}
"""

GET_PRODUCT_OPTIONS_QUERY = """
query GetProductOptions($productQid: String!) {
    findAllOptionsForProduct(productQid: $productQid) {
        id
        qid
        name
        type
        values
        productId
        createdAt
        updatedAt
    }
}
"""

GET_OPTION_BY_QID_QUERY = """
query GetOptionByQid($optionQid: String!) {
    findOptionByQid(optionQid: $optionQid) {
        id
        qid
        name
        type
        values
        productId
        product {
            id
            qid
            title
        }
        createdAt
        updatedAt
    }
}
"""


# ============================================================
# 🚀 FUNCTIONS - دوال الاستعلام
# ============================================================

class ProductQueryService:
    """
    خدمة استعلامات المنتجات
    تحتوي على جميع دوال جلب بيانات المنتجات
    """
    
    def __init__(self):
        self.client = QomrahGraphQLClient()
    
    # ============================================================
    # 📦 PRODUCT QUERIES - استعلامات المنتج
    # ============================================================
    
    def get_product_by_qid(self, qid: str) -> Optional[Dict]:
        """
        جلب منتج بواسطة QID مع جميع الحقول
        
        Args:
            qid: معرف المنتج
        
        Returns:
            Dict: بيانات المنتج الكاملة
        """
        result = self.client.execute_query(GET_PRODUCT_DETAIL_QUERY, {"qid": qid})
        return result.get('findProductByQid') if result else None
    
    def get_all_products(self, page: int = 1, limit: int = 50, 
                         title: str = None, status: str = None,
                         collection_qid: str = None) -> Dict:
        """
        جلب جميع المنتجات مع فلترة
        
        Args:
            page: رقم الصفحة
            limit: عدد المنتجات في الصفحة
            title: فلترة حسب الاسم
            status: فلترة حسب الحالة
            collection_qid: فلترة حسب المجموعة
        
        Returns:
            Dict: {data: List[Dict], pagination: Dict}
        """
        variables = {"page": page, "limit": limit}
        if title:
            variables["title"] = title
        if status:
            variables["status"] = status
        if collection_qid:
            variables["collectionQid"] = collection_qid
        
        result = self.client.execute_query(GET_ALL_PRODUCTS_QUERY, variables)
        
        if result:
            products = result.get('findAllProducts', [])
            return {
                "data": products,
                "pagination": {
                    "currentPage": page,
                    "limit": limit,
                    "total": len(products)
                }
            }
        return {"data": [], "pagination": None}
    
    def get_all_products_flat(self, limit: int = 50, **filters) -> List[Dict]:
        """
        جلب جميع المنتجات في قائمة واحدة (عبر جميع الصفحات)
        
        Args:
            limit: عدد المنتجات في الصفحة
            **filters: فلترات إضافية
        
        Returns:
            List[Dict]: قائمة بجميع المنتجات
        """
        all_products = []
        page = 1
        
        while True:
            result = self.get_all_products(page=page, limit=limit, **filters)
            products = result.get('data', [])
            
            if not products:
                break
            
            all_products.extend(products)
            page += 1
        
        return all_products
    
    def get_product_status(self, qid: str) -> Optional[Dict]:
        """
        جلب حالة المنتج
        
        Args:
            qid: معرف المنتج
        
        Returns:
            Dict: {id, status, publishedAt, updatedAt}
        """
        result = self.client.execute_query(GET_PRODUCT_STATUS_QUERY, {"qid": qid})
        return result.get('findProductStatus') if result else None
    
    def get_top_viewed_products(self, limit: int = 10) -> List[Dict]:
        """
        جلب المنتجات الأكثر مشاهدة
        
        Args:
            limit: عدد المنتجات
        
        Returns:
            List[Dict]: قائمة المنتجات
        """
        result = self.client.execute_query(GET_TOP_VIEWED_PRODUCTS_QUERY, {"limit": limit})
        return result.get('FindTopViewedProducts', []) if result else []
    
    # ============================================================
    # 🎨 VARIANT QUERIES - استعلامات الفاريانتات
    # ============================================================
    
    def get_product_variants(self, product_qid: str) -> List[Dict]:
        """
        جلب جميع الفاريانتات لمنتج
        
        Args:
            product_qid: معرف المنتج
        
        Returns:
            List[Dict]: قائمة الفاريانتات
        """
        result = self.client.execute_query(GET_PRODUCT_VARIANTS_QUERY, {"productQid": product_qid})
        return result.get('findAllVariantsByProductId', []) if result else []
    
    def get_variant_by_id(self, variant_qid: str) -> Optional[Dict]:
        """
        جلب فاريانت بواسطة QID
        
        Args:
            variant_qid: معرف الفاريانت
        
        Returns:
            Dict: بيانات الفاريانت
        """
        result = self.client.execute_query(GET_VARIANT_BY_ID_QUERY, {"variantQid": variant_qid})
        return result.get('findVariantById') if result else None
    
    # ============================================================
    # 🎯 OPTION QUERIES - استعلامات الخيارات
    # ============================================================
    
    def get_product_options(self, product_qid: str) -> List[Dict]:
        """
        جلب جميع خيارات المنتج
        
        Args:
            product_qid: معرف المنتج
        
        Returns:
            List[Dict]: قائمة الخيارات
        """
        result = self.client.execute_query(GET_PRODUCT_OPTIONS_QUERY, {"productQid": product_qid})
        return result.get('findAllOptionsForProduct', []) if result else []
    
    def get_option_by_qid(self, option_qid: str) -> Optional[Dict]:
        """
        جلب خيار بواسطة QID
        
        Args:
            option_qid: معرف الخيار
        
        Returns:
            Dict: بيانات الخيار
        """
        result = self.client.execute_query(GET_OPTION_BY_QID_QUERY, {"optionQid": option_qid})
        return result.get('findOptionByQid') if result else None
    
    # ============================================================
    # 📊 STATISTICS - إحصائيات
    # ============================================================
    
    def get_product_stats(self) -> Dict:
        """
        الحصول على إحصائيات المنتجات
        
        Returns:
            Dict: {total, active, inactive, draft, archived, totalViews}
        """
        try:
            all_products = self.get_all_products_flat(limit=100)
            
            stats = {
                'total': len(all_products),
                'active': 0,
                'inactive': 0,
                'draft': 0,
                'archived': 0,
                'totalViews': 0,
                'totalQuantity': 0
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
                
                stats['totalViews'] += product.get('views', 0)
                stats['totalQuantity'] += product.get('quantity', 0)
            
            return stats
            
        except Exception as e:
            print(f"❌ خطأ في get_product_stats: {e}")
            return {'total': 0, 'active': 0, 'inactive': 0, 'draft': 0, 'archived': 0, 'totalViews': 0, 'totalQuantity': 0}
    
    def search_products(self, query_text: str, limit: int = 20) -> List[Dict]:
        """
        البحث عن منتجات
        
        Args:
            query_text: نص البحث
            limit: عدد النتائج
        
        Returns:
            List[Dict]: قائمة المنتجات المطابقة
        """
        # استخدام فلتر title للبحث
        return self.get_all_products_flat(limit=limit, title=query_text)
    
    def get_products_by_collection(self, collection_qid: str) -> List[Dict]:
        """
        جلب منتجات مجموعة معينة
        
        Args:
            collection_qid: معرف المجموعة
        
        Returns:
            List[Dict]: قائمة المنتجات
        """
        return self.get_all_products_flat(limit=100, collection_qid=collection_qid)
    
    def get_products_by_status(self, status: str) -> List[Dict]:
        """
        جلب منتجات حسب الحالة
        
        Args:
            status: الحالة (ACTIVE, INACTIVE, DRAFT, ARCHIVED)
        
        Returns:
            List[Dict]: قائمة المنتجات
        """
        return self.get_all_products_flat(limit=100, status=status)


# ============================================================
# 🚀 SINGLETON INSTANCE
# ============================================================

product_query = ProductQueryService()


# ============================================================
# 📋 EXPORTS - للاستخدام المباشر
# ============================================================

__all__ = [
    'GET_PRODUCT_DETAIL_QUERY',
    'GET_ALL_PRODUCTS_QUERY',
    'GET_PRODUCT_STATUS_QUERY',
    'GET_TOP_VIEWED_PRODUCTS_QUERY',
    'GET_PRODUCT_VARIANTS_QUERY',
    'GET_VARIANT_BY_ID_QUERY',
    'GET_PRODUCT_OPTIONS_QUERY',
    'GET_OPTION_BY_QID_QUERY',
    'ProductQueryService',
    'product_query'
]


# ============================================================
# 🧪 TEST - اختبار سريع (اختياري)
# ============================================================

if __name__ == "__main__":
    # اختبار جلب منتج
    service = ProductQueryService()
    
    # جلب منتج بواسطة QID (استخدم QID حقيقي)
    # product = service.get_product_by_qid("test_qid")
    # print(product)
    
    # جلب جميع المنتجات
    products = service.get_all_products(limit=5)
    print(f"✅ تم جلب {len(products.get('data', []))} منتج")
    
    # إحصائيات
    stats = service.get_product_stats()
    print(f"📊 الإحصائيات: {stats}")
