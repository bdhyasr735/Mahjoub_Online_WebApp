# coding: utf-8
# 📂 apps/services/fetch_collections_data.graphql.py

from typing import Dict, List, Optional, Any
from .graphql_client import QomrahGraphQLClient


# ============================================================
# 📋 QUERIES - استعلامات المجموعات
# ============================================================

GET_ALL_COLLECTIONS_QUERY = """
query GetAllCollections($page: Int, $limit: Int, $title: String, $sortBy: String, $sortOrder: String) {
    findAllCollections(page: $page, limit: $limit, title: $title, sortBy: $sortBy, sortOrder: $sortOrder) {
        id
        qid
        app
        title
        slug
        handle
        description
        operation
        productCount
        products {
            id
            qid
            title
            slug
            price
            status
            images {
                _id
                fileUrl
            }
        }
        image {
            _id
            fileUrl
            title
            description
            mimetype
            sizeInKB
            sizeInMB
        }
        conditions {
            price {
                start
                end
            }
            discount {
                type
                value
            }
        }
        seo {
            title
            description
            keywords
            image
            canonicalUrl
        }
        createdAt
        updatedAt
    }
}
"""

GET_COLLECTION_BY_QID_QUERY = """
query GetCollectionByQid($qid: String!) {
    findCollectionByQid(qid: $qid) {
        id
        qid
        app
        title
        slug
        handle
        description
        operation
        productCount
        products {
            id
            qid
            title
            slug
            description
            price
            compareAtPrice
            status
            quantity
            images {
                _id
                fileUrl
            }
            variants {
                id
                qid
                price
                quantity
            }
            collections {
                qid
                title
                slug
            }
            createdAt
            updatedAt
        }
        image {
            _id
            fileUrl
            title
            description
            mimetype
            sizeInKB
            sizeInMB
        }
        conditions {
            price {
                start
                end
            }
            discount {
                type
                value
            }
        }
        seo {
            title
            description
            keywords
            image
            canonicalUrl
        }
        createdAt
        updatedAt
    }
}
"""

GET_PRODUCTS_FOR_COLLECTION_QUERY = """
query GetProductsForCollection($collectionQid: String!, $page: Int, $limit: Int) {
    findAllProductsForCollection(collectionQid: $collectionQid, page: $page, limit: $limit) {
        id
        qid
        title
        slug
        description
        price
        compareAtPrice
        status
        quantity
        images {
            _id
            fileUrl
        }
        variants {
            id
            qid
            price
            quantity
        }
        createdAt
        updatedAt
    }
}
"""


# ============================================================
# ✏️ MUTATIONS - تحويرات المجموعات
# ============================================================

CREATE_COLLECTION_MUTATION = """
mutation CreateCollection($input: CreateCollectionInput!) {
    createCollection(input: $input) {
        id
        qid
        title
        slug
        description
        image {
            _id
            fileUrl
        }
        productCount
        createdAt
    }
}
"""

UPDATE_COLLECTION_MUTATION = """
mutation UpdateCollection($qid: String!, $input: UpdateCollectionInput!) {
    updateCollection(qid: $qid, input: $input) {
        id
        qid
        title
        slug
        description
        image {
            _id
            fileUrl
        }
        updatedAt
    }
}
"""

REMOVE_COLLECTION_MUTATION = """
mutation RemoveCollection($qid: String!) {
    removeCollection(qid: $qid)
}
"""

ADD_PRODUCT_TO_COLLECTIONS_MUTATION = """
mutation AddProductToCollections($productQid: String!, $collectionQids: [String!]!) {
    AddProductToCollections(productQid: $productQid, collectionQids: $collectionQids) {
        id
        qid
        collections {
            id
            qid
            title
            slug
        }
        updatedAt
    }
}
"""


# ============================================================
# 🚀 FUNCTIONS - دوال المجموعات
# ============================================================

class CollectionQueryService:
    """
    خدمة استعلامات وتحويرات المجموعات
    تحتوي على جميع دوال جلب وإنشاء وتحديث وحذف المجموعات
    """
    
    def __init__(self):
        self.client = QomrahGraphQLClient()
    
    # ============================================================
    # 📂 COLLECTION QUERIES - استعلامات المجموعات
    # ============================================================
    
    def get_all_collections(self, page: int = 1, limit: int = 50,
                           title: str = None, sort_by: str = None,
                           sort_order: str = None) -> Dict:
        """
        جلب جميع المجموعات مع فلترة
        
        Args:
            page: رقم الصفحة
            limit: عدد المجموعات في الصفحة
            title: فلترة حسب الاسم
            sort_by: ترتيب حسب (title, createdAt, updatedAt, productCount)
            sort_order: اتجاه الترتيب (ASC, DESC)
        
        Returns:
            Dict: {data: List[Dict], pagination: Dict}
        """
        variables = {"page": page, "limit": limit}
        if title:
            variables["title"] = title
        if sort_by:
            variables["sortBy"] = sort_by
        if sort_order:
            variables["sortOrder"] = sort_order
        
        result = self.client.execute_query(GET_ALL_COLLECTIONS_QUERY, variables)
        
        if result:
            collections = result.get('findAllCollections', [])
            return {
                "data": collections,
                "pagination": {
                    "currentPage": page,
                    "limit": limit,
                    "total": len(collections)
                }
            }
        return {"data": [], "pagination": None}
    
    def get_all_collections_flat(self, limit: int = 100, **filters) -> List[Dict]:
        """
        جلب جميع المجموعات في قائمة واحدة (عبر جميع الصفحات)
        
        Args:
            limit: عدد المجموعات في الصفحة
            **filters: فلترات إضافية (title, sort_by, sort_order)
        
        Returns:
            List[Dict]: قائمة بجميع المجموعات
        """
        all_collections = []
        page = 1
        
        while True:
            result = self.get_all_collections(page=page, limit=limit, **filters)
            collections = result.get('data', [])
            
            if not collections:
                break
            
            all_collections.extend(collections)
            page += 1
        
        return all_collections
    
    def get_collection_by_qid(self, qid: str) -> Optional[Dict]:
        """
        جلب مجموعة بواسطة QID مع جميع المنتجات
        
        Args:
            qid: معرف المجموعة
        
        Returns:
            Dict: بيانات المجموعة الكاملة
        """
        result = self.client.execute_query(GET_COLLECTION_BY_QID_QUERY, {"qid": qid})
        return result.get('findCollectionByQid') if result else None
    
    def get_products_for_collection(self, collection_qid: str,
                                   page: int = 1, limit: int = 50) -> List[Dict]:
        """
        جلب منتجات مجموعة معينة
        
        Args:
            collection_qid: معرف المجموعة
            page: رقم الصفحة
            limit: عدد المنتجات في الصفحة
        
        Returns:
            List[Dict]: قائمة المنتجات
        """
        result = self.client.execute_query(
            GET_PRODUCTS_FOR_COLLECTION_QUERY,
            {"collectionQid": collection_qid, "page": page, "limit": limit}
        )
        return result.get('findAllProductsForCollection', []) if result else []
    
    # ============================================================
    # ✏️ COLLECTION MUTATIONS - تحويرات المجموعات
    # ============================================================
    
    def create_collection(self, title: str, description: str = "",
                          image: str = None, conditions: Dict = None,
                          seo: Dict = None, **kwargs) -> Dict:
        """
        إنشاء مجموعة جديدة
        
        Args:
            title: اسم المجموعة
            description: وصف المجموعة
            image: رابط الصورة
            conditions: شروط المجموعة {price: {start, end}, discount: {type, value}}
            seo: بيانات SEO
            **kwargs: حقول إضافية
        
        Returns:
            Dict: {success: bool, qid: str, message: str, data: dict}
        """
        try:
            input_data = {
                "title": title,
                "description": description
            }
            
            if image:
                input_data["image"] = image
            if conditions:
                input_data["conditions"] = conditions
            if seo:
                input_data["seo"] = seo
            if kwargs.get('slug'):
                input_data["slug"] = kwargs.get('slug')
            if kwargs.get('handle'):
                input_data["handle"] = kwargs.get('handle')
            if kwargs.get('operation'):
                input_data["operation"] = kwargs.get('operation')
            
            print(f"🔄 جاري إنشاء المجموعة: {title}")
            result = self.client.execute_query(CREATE_COLLECTION_MUTATION, {"input": input_data})
            
            if result:
                data = result.get('createCollection', {})
                if data:
                    qid = data.get('qid')
                    print(f"✅ تم إنشاء المجموعة بنجاح بـ QID: {qid}")
                    return {
                        'success': True,
                        'qid': qid,
                        'message': 'تم إنشاء المجموعة بنجاح',
                        'data': data
                    }
            
            return {
                'success': False,
                'message': 'فشل إنشاء المجموعة',
                'qid': None,
                'data': None
            }
            
        except Exception as e:
            print(f"❌ خطأ في create_collection: {e}")
            return {
                'success': False,
                'message': f'خطأ: {str(e)}',
                'qid': None,
                'data': None
            }
    
    def update_collection(self, qid: str, title: str = None,
                          description: str = None, image: str = None,
                          conditions: Dict = None, seo: Dict = None,
                          **kwargs) -> bool:
        """
        تحديث مجموعة
        
        Args:
            qid: معرف المجموعة
            title: الاسم الجديد
            description: الوصف الجديد
            image: رابط الصورة الجديد
            conditions: شروط جديدة
            seo: بيانات SEO جديدة
            **kwargs: حقول إضافية
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        try:
            input_data = {}
            
            if title is not None:
                input_data["title"] = title
            if description is not None:
                input_data["description"] = description
            if image is not None:
                input_data["image"] = image
            if conditions is not None:
                input_data["conditions"] = conditions
            if seo is not None:
                input_data["seo"] = seo
            if kwargs.get('slug'):
                input_data["slug"] = kwargs.get('slug')
            if kwargs.get('handle'):
                input_data["handle"] = kwargs.get('handle')
            
            if not input_data:
                print("⚠️ لا توجد بيانات للتحديث")
                return False
            
            print(f"🔄 جاري تحديث المجموعة {qid}")
            result = self.client.execute_query(
                UPDATE_COLLECTION_MUTATION,
                {"qid": qid, "input": input_data}
            )
            
            if result and result.get('updateCollection'):
                print(f"✅ تم تحديث المجموعة بنجاح")
                return True
            else:
                print(f"❌ فشل تحديث المجموعة")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في update_collection: {e}")
            return False
    
    def remove_collection(self, qid: str) -> bool:
        """
        حذف مجموعة
        
        Args:
            qid: معرف المجموعة
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        try:
            print(f"🔄 جاري حذف المجموعة {qid}")
            result = self.client.execute_query(REMOVE_COLLECTION_MUTATION, {"qid": qid})
            
            if result and result.get('removeCollection') is True:
                print(f"✅ تم حذف المجموعة بنجاح")
                return True
            else:
                print(f"❌ فشل حذف المجموعة")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في remove_collection: {e}")
            return False
    
    def add_product_to_collections(self, product_qid: str,
                                   collection_qids: List[str]) -> bool:
        """
        إضافة منتج إلى مجموعات
        
        Args:
            product_qid: معرف المنتج
            collection_qids: قائمة معرفات المجموعات
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        try:
            print(f"🔄 جاري إضافة المنتج {product_qid} إلى {len(collection_qids)} مجموعة")
            result = self.client.execute_query(
                ADD_PRODUCT_TO_COLLECTIONS_MUTATION,
                {"productQid": product_qid, "collectionQids": collection_qids}
            )
            
            if result and result.get('AddProductToCollections'):
                print(f"✅ تم إضافة المنتج إلى المجموعات بنجاح")
                return True
            else:
                print(f"❌ فشل إضافة المنتج إلى المجموعات")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في add_product_to_collections: {e}")
            return False
    
    # ============================================================
    # 📊 STATISTICS - إحصائيات المجموعات
    # ============================================================
    
    def get_collection_stats(self) -> Dict:
        """
        الحصول على إحصائيات المجموعات
        
        Returns:
            Dict: {total, totalProducts, collectionsWithProducts, emptyCollections}
        """
        try:
            collections = self.get_all_collections_flat(limit=100)
            
            stats = {
                'total': len(collections),
                'totalProducts': 0,
                'collectionsWithProducts': 0,
                'emptyCollections': 0
            }
            
            for collection in collections:
                product_count = collection.get('productCount', 0)
                stats['totalProducts'] += product_count
                if product_count > 0:
                    stats['collectionsWithProducts'] += 1
                else:
                    stats['emptyCollections'] += 1
            
            return stats
            
        except Exception as e:
            print(f"❌ خطأ في get_collection_stats: {e}")
            return {'total': 0, 'totalProducts': 0, 'collectionsWithProducts': 0, 'emptyCollections': 0}
    
    def search_collections(self, query_text: str, limit: int = 20) -> List[Dict]:
        """
        البحث عن مجموعات
        
        Args:
            query_text: نص البحث
            limit: عدد النتائج
        
        Returns:
            List[Dict]: قائمة المجموعات المطابقة
        """
        return self.get_all_collections_flat(limit=limit, title=query_text)


# ============================================================
# 🚀 SINGLETON INSTANCE
# ============================================================

collection_query = CollectionQueryService()


# ============================================================
# 📋 EXPORTS - للاستخدام المباشر
# ============================================================

__all__ = [
    'GET_ALL_COLLECTIONS_QUERY',
    'GET_COLLECTION_BY_QID_QUERY',
    'GET_PRODUCTS_FOR_COLLECTION_QUERY',
    'CREATE_COLLECTION_MUTATION',
    'UPDATE_COLLECTION_MUTATION',
    'REMOVE_COLLECTION_MUTATION',
    'ADD_PRODUCT_TO_COLLECTIONS_MUTATION',
    'CollectionQueryService',
    'collection_query'
]


# ============================================================
# 🧪 TEST - اختبار سريع (اختياري)
# ============================================================

if __name__ == "__main__":
    service = CollectionQueryService()
    
    # جلب جميع المجموعات
    collections = service.get_all_collections(limit=5)
    print(f"✅ تم جلب {len(collections.get('data', []))} مجموعة")
    
    # إحصائيات
    stats = service.get_collection_stats()
    print(f"📊 الإحصائيات: {stats}")
