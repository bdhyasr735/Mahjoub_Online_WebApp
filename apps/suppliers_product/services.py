# coding: utf-8
# 📂 apps/suppliers_product/services.py

from core.graphql_client import GraphQLClient
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)

# ============================================
# استعلامات GraphQL
# ============================================

# 1. جلب جميع المنتجات
GET_ALL_PRODUCTS = """
query FindAllProducts($input: GetAllProductsInput) {
  findAllProducts(input: $input) {
    id qid name description handle status isActive isAvailable
    price compareAtPrice costPerItem currency quantity
    sku barcode weight weightUnit createdAt updatedAt publishedAt
    inventory { id quantity available reserved location warehouse }
    mainImage { id url altText width height }
    images { id url altText width height position }
    options { id name values { id value hexCode image { url } } }
    variants {
      id sku price compareAtPrice quantity isAvailable
      options { name value }
      image { url altText }
      inventory { quantity available reserved }
    }
    collections { id name handle }
    category { id name handle }
    brand { id name logo { url } }
    ratings { average count }
  }
}
"""

# 2. جلب منتج بواسطة QID
GET_PRODUCT_BY_QID = """
query FindProductByQid($qid: String!) {
  findProductByQid(qid: $qid) {
    id qid name description handle status isActive isAvailable
    price compareAtPrice costPerItem currency quantity
    sku barcode weight weightUnit createdAt updatedAt publishedAt
    inventory { id quantity available reserved location warehouse }
    mainImage { id url altText width height }
    images { id url altText width height position }
    media { id url altText type position createdAt }
    options { id name values { id value hexCode image { url } } }
    variants {
      id sku price compareAtPrice quantity isAvailable
      options { name value }
      image { url altText }
      inventory { quantity available reserved location }
    }
    collections { id name handle }
    category { id name handle }
    brand { id name logo { url } }
    ratings { average count }
    seo { title description }
    translations { locale name description }
    metafields { namespace key value }
  }
}
"""

# 3. جلب المتغيرات
GET_VARIANTS = """
query FindAllVariantsByProductId($productId: ID!) {
  findAllVariantsByProductId(productId: $productId) {
    id sku price compareAtPrice quantity isAvailable
    options { name value }
    image { url altText }
    inventory { quantity available reserved }
  }
}
"""

# 4. جلب المخزون فقط
GET_PRODUCT_INVENTORY = """
query GetProductInventory($productId: ID!) {
  findProductByQid(qid: $productId) {
    id qid name quantity
    inventory { id quantity available reserved location warehouse }
    variants {
      id sku price quantity isAvailable
      options { name value }
      inventory { id quantity available reserved location warehouse }
    }
  }
}
"""

# 5. جلب الألوان والأسعار
GET_PRODUCT_COLORS_PRICES = """
query GetProductColorsAndPrices($qid: String!) {
  findProductByQid(qid: $qid) {
    id qid name price compareAtPrice currency
    options { id name values { id value hexCode image { url } } }
    variants {
      id sku price compareAtPrice quantity isAvailable
      options { name value }
      image { url altText }
      inventory { quantity available }
    }
  }
}
"""

# 6. جلب الصور والمكتبة
GET_PRODUCT_MEDIA = """
query GetProductMedia($productId: ID!) {
  findProductByQid(qid: $productId) {
    id qid name
    mainImage { id url altText width height }
    images { id url altText width height position }
    media { id url altText type position createdAt }
    variants { id image { url altText } options { name value } }
  }
}
"""

# 7. جلب حالة المنتج
GET_PRODUCT_STATUS = """
query FindProductStatus {
  findProductStatus {
    id qid name status isActive isAvailable isPublished isDraft isArchived
    createdAt updatedAt
  }
}
"""

# 8. جلب الأكثر مشاهدة
GET_TOP_VIEWED = """
query FindTopViewedProducts {
  FindTopViewedProducts {
    id qid name price compareAtPrice views
    mainImage { url }
    ratings { average count }
  }
}
"""

# 9. جلب منتجات المجموعة
GET_PRODUCTS_BY_COLLECTION = """
query FindAllProductsForCollection($id: ID!) {
  findAllProductsForCollection(id: $id) {
    id qid name description price compareAtPrice
    sku quantity status isActive isAvailable
    mainImage { id url altText }
    variants { id sku price quantity isAvailable image { url } inventory { quantity available } }
    category { id name }
    brand { id name logo { url } }
    ratings { average count }
    inventory { quantity available }
  }
}
"""


# ============================================
# تهيئة عميل GraphQL
# ============================================

_graphql_client = None

def get_graphql_client():
    """الحصول على عميل GraphQL (Singleton)"""
    global _graphql_client
    if _graphql_client is None:
        _graphql_client = GraphQLClient()
    return _graphql_client


# ============================================
# 1. جلب جميع المنتجات
# ============================================

def fetch_all_products(input_data: Optional[Dict] = None) -> List[Dict]:
    """جلب جميع المنتجات من GraphQL"""
    try:
        client = get_graphql_client()
        result = client.execute(GET_ALL_PRODUCTS, {"input": input_data or {}})
        return result.get('findAllProducts', [])
    except Exception as e:
        logger.error(f"❌ fetch_all_products: {e}")
        return []


# ============================================
# 2. جلب منتج بواسطة QID
# ============================================

def fetch_product_by_qid(qid: str) -> Optional[Dict]:
    """جلب منتج بواسطة QID"""
    try:
        client = get_graphql_client()
        result = client.execute(GET_PRODUCT_BY_QID, {"qid": qid})
        return result.get('findProductByQid')
    except Exception as e:
        logger.error(f"❌ fetch_product_by_qid ({qid}): {e}")
        return None


# ============================================
# 3. جلب متغيرات المنتج
# ============================================

def fetch_product_variants(product_id: str) -> List[Dict]:
    """جلب متغيرات المنتج"""
    try:
        client = get_graphql_client()
        result = client.execute(GET_VARIANTS, {"productId": product_id})
        return result.get('findAllVariantsByProductId', [])
    except Exception as e:
        logger.error(f"❌ fetch_product_variants: {e}")
        return []


# ============================================
# 4. جلب المخزون فقط
# ============================================

def fetch_product_inventory(product_id: str) -> Optional[Dict]:
    """جلب المخزون فقط"""
    try:
        client = get_graphql_client()
        result = client.execute(GET_PRODUCT_INVENTORY, {"productId": product_id})
        return result.get('findProductByQid')
    except Exception as e:
        logger.error(f"❌ fetch_product_inventory: {e}")
        return None


# ============================================
# 5. جلب الألوان والأسعار
# ============================================

def fetch_product_colors_prices(qid: str) -> Optional[Dict]:
    """جلب الألوان والأسعار"""
    try:
        client = get_graphql_client()
        result = client.execute(GET_PRODUCT_COLORS_PRICES, {"qid": qid})
        return result.get('findProductByQid')
    except Exception as e:
        logger.error(f"❌ fetch_product_colors_prices: {e}")
        return None


# ============================================
# 6. جلب الصور والمكتبة
# ============================================

def fetch_product_media(product_id: str) -> Optional[Dict]:
    """جلب الصور والمكتبة"""
    try:
        client = get_graphql_client()
        result = client.execute(GET_PRODUCT_MEDIA, {"productId": product_id})
        return result.get('findProductByQid')
    except Exception as e:
        logger.error(f"❌ fetch_product_media: {e}")
        return None


# ============================================
# 7. جلب حالة المنتج
# ============================================

def fetch_product_status() -> List[Dict]:
    """جلب حالة المنتجات"""
    try:
        client = get_graphql_client()
        result = client.execute(GET_PRODUCT_STATUS)
        return result.get('findProductStatus', [])
    except Exception as e:
        logger.error(f"❌ fetch_product_status: {e}")
        return []


# ============================================
# 8. جلب الأكثر مشاهدة
# ============================================

def fetch_top_viewed() -> List[Dict]:
    """جلب المنتجات الأكثر مشاهدة"""
    try:
        client = get_graphql_client()
        result = client.execute(GET_TOP_VIEWED)
        return result.get('FindTopViewedProducts', [])
    except Exception as e:
        logger.error(f"❌ fetch_top_viewed: {e}")
        return []


# ============================================
# 9. جلب منتجات المجموعة
# ============================================

def fetch_products_by_collection(collection_id: str) -> List[Dict]:
    """جلب منتجات المجموعة"""
    try:
        client = get_graphql_client()
        result = client.execute(GET_PRODUCTS_BY_COLLECTION, {"id": collection_id})
        return result.get('findAllProductsForCollection', [])
    except Exception as e:
        logger.error(f"❌ fetch_products_by_collection: {e}")
        return []


# ============================================
# 10. البحث عن منتجات
# ============================================

def search_products(search_term: str, limit: int = 20) -> List[Dict]:
    """البحث عن منتجات"""
    try:
        return fetch_all_products({
            "search": search_term,
            "limit": limit,
            "isActive": True
        })
    except Exception as e:
        logger.error(f"❌ search_products: {e}")
        return []


# ============================================
# 11. جلب المنتجات حسب النطاق السعري
# ============================================

def fetch_products_by_price_range(min_price: float, max_price: float) -> List[Dict]:
    """جلب المنتجات حسب النطاق السعري"""
    try:
        return fetch_all_products({
            "minPrice": min_price,
            "maxPrice": max_price,
            "isActive": True
        })
    except Exception as e:
        logger.error(f"❌ fetch_products_by_price_range: {e}")
        return []


# ============================================
# 12. جلب المنتجات النشطة
# ============================================

def fetch_active_products(limit: int = 50) -> List[Dict]:
    """جلب المنتجات النشطة"""
    try:
        return fetch_all_products({
            "limit": limit,
            "isActive": True
        })
    except Exception as e:
        logger.error(f"❌ fetch_active_products: {e}")
        return []
