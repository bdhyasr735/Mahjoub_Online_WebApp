# coding: utf-8
# 📂 apps/suppliers_product/sync_suppliers_product.py

"""
واجهة (Interface) لخدمة عرض وإدارة منتجات الموردين
تستخدم كطبقة وسيطة بين الـ Routes والـ Service
"""

from apps.suppliers_product.services.product_sync_service import supplier_product
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


# ============================================================
# 📦 PRODUCT OPERATIONS - عمليات المنتجات
# ============================================================

def get_products(supplier_id: int, search: str = None) -> List[Dict]:
    """
    جلب قائمة منتجات المورد
    
    Args:
        supplier_id: معرف المورد
        search: نص البحث (اختياري)
    
    Returns:
        List[Dict]: قائمة المنتجات مع بياناتها
    """
    try:
        # جلب العلاقات من الخدمة
        mappings = supplier_product.get_supplier_mappings(supplier_id)
        
        if not mappings:
            return []
        
        products = []
        for mapping in mappings:
            # جلب بيانات المنتج من قمرة
            product = supplier_product.fetch_product_by_qid(mapping.get('qid'))
            if product:
                # فلترة حسب البحث
                if search:
                    search_lower = search.lower()
                    title = product.get('title', '').lower()
                    qid = product.get('qid', '').lower()
                    sku = product.get('identification', {}).get('sku', '').lower()
                    
                    if search_lower not in title and search_lower not in qid and search_lower not in sku:
                        continue
                
                products.append({
                    'qid': mapping.get('qid'),
                    'product': product,
                    'mapping_id': mapping.get('id'),
                    'supplier_id': mapping.get('supplier_id'),
                    'supplier_name': mapping.get('supplier_name'),
                    'status': mapping.get('status'),
                    'created_at': mapping.get('created_at'),
                    'updated_at': mapping.get('updated_at')
                })
        
        return products
    
    except Exception as e:
        logger.error(f"❌ خطأ في get_products: {e}")
        return []


def get_product_stats(supplier_id: int) -> Dict:
    """
    جلب إحصائيات منتجات المورد
    
    Args:
        supplier_id: معرف المورد
    
    Returns:
        Dict: {
            'total': int,
            'active': int,
            'draft': int,
            'inactive': int,
            'archived': int
        }
    """
    try:
        products = get_products(supplier_id)
        
        stats = {
            'total': len(products),
            'active': 0,
            'draft': 0,
            'inactive': 0,
            'archived': 0,
            'pending': 0
        }
        
        for item in products:
            status = item.get('product', {}).get('status', '').upper()
            if status in ['ACTIVE', 'PUBLISHED']:
                stats['active'] += 1
            elif status == 'DRAFT':
                stats['draft'] += 1
            elif status == 'INACTIVE':
                stats['inactive'] += 1
            elif status == 'ARCHIVED':
                stats['archived'] += 1
            elif status == 'PENDING':
                stats['pending'] += 1
        
        return stats
    
    except Exception as e:
        logger.error(f"❌ خطأ في get_product_stats: {e}")
        return {
            'total': 0,
            'active': 0,
            'draft': 0,
            'inactive': 0,
            'archived': 0,
            'pending': 0
        }


def get_suppliers_list() -> List[Dict]:
    """
    جلب قائمة الموردين النشطين
    
    Returns:
        List[Dict]: قائمة الموردين
    """
    return supplier_product.get_active_suppliers()


def get_supplier_info(supplier_id: int) -> Dict:
    """
    جلب بيانات مورد محدد
    
    Args:
        supplier_id: معرف المورد
    
    Returns:
        Dict: بيانات المورد
    """
    return supplier_product.get_supplier(supplier_id)


def get_product_by_qid(qid: str, supplier_id: int) -> Optional[Dict]:
    """
    جلب منتج محدد مع التحقق من الصلاحية
    
    Args:
        qid: معرف المنتج في قمرة
        supplier_id: معرف المورد
    
    Returns:
        Dict: بيانات المنتج أو None
    """
    result = supplier_product.get_product(qid, supplier_id)
    if result.get('success'):
        return result.get('product')
    return None


def get_product_with_mapping(qid: str, supplier_id: int) -> Dict:
    """
    جلب منتج مع بيانات الربط
    
    Args:
        qid: معرف المنتج في قمرة
        supplier_id: معرف المورد
    
    Returns:
        Dict: {success: bool, product: dict, mapping: dict, error: str}
    """
    return supplier_product.get_product(qid, supplier_id)


# ============================================================
# 📊 FILTER OPERATIONS - عمليات الفلترة
# ============================================================

def filter_products(products: List[Dict], status: str = None, 
                    min_price: float = None, max_price: float = None) -> List[Dict]:
    """
    فلترة المنتجات حسب المعايير
    
    Args:
        products: قائمة المنتجات
        status: حالة المنتج (ACTIVE, DRAFT, etc.)
        min_price: الحد الأدنى للسعر
        max_price: الحد الأقصى للسعر
    
    Returns:
        List[Dict]: قائمة المنتجات المفلترة
    """
    filtered = products.copy()
    
    if status:
        status_upper = status.upper()
        filtered = [
            p for p in filtered 
            if p.get('product', {}).get('status', '').upper() == status_upper
        ]
    
    if min_price is not None or max_price is not None:
        filtered = [
            p for p in filtered 
            if p.get('product', {}).get('price', 0) is not None
        ]
        
        if min_price is not None:
            filtered = [
                p for p in filtered 
                if p.get('product', {}).get('price', 0) >= min_price
            ]
        
        if max_price is not None:
            filtered = [
                p for p in filtered 
                if p.get('product', {}).get('price', 0) <= max_price
            ]
    
    return filtered


def search_products(products: List[Dict], query: str) -> List[Dict]:
    """
    البحث في المنتجات
    
    Args:
        products: قائمة المنتجات
        query: نص البحث
    
    Returns:
        List[Dict]: قائمة المنتجات المطابقة
    """
    if not query:
        return products
    
    query_lower = query.lower()
    results = []
    
    for item in products:
        product = item.get('product', {})
        title = product.get('title', '').lower()
        description = product.get('description', '').lower()
        sku = product.get('identification', {}).get('sku', '').lower()
        qid = item.get('qid', '').lower()
        
        if (query_lower in title or 
            query_lower in description or 
            query_lower in sku or 
            query_lower in qid):
            results.append(item)
    
    return results


def paginate_products(products: List[Dict], page: int = 1, limit: int = 20) -> Dict:
    """
    تقسيم المنتجات إلى صفحات
    
    Args:
        products: قائمة المنتجات
        page: رقم الصفحة
        limit: عدد العناصر في الصفحة
    
    Returns:
        Dict: {
            'items': List[Dict],
            'total': int,
            'page': int,
            'limit': int,
            'total_pages': int
        }
    """
    total = len(products)
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    
    # التأكد من أن الصفحة ضمن النطاق
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages
    
    start = (page - 1) * limit
    end = start + limit
    
    return {
        'items': products[start:end],
        'total': total,
        'page': page,
        'limit': limit,
        'total_pages': total_pages
    }


# ============================================================
# 🗑️ DELETE OPERATIONS - عمليات الحذف
# ============================================================

def delete_product(qid: str, supplier_id: int) -> Dict:
    """
    حذف منتج مع التحقق من الصلاحية
    
    Args:
        qid: معرف المنتج في قمرة
        supplier_id: معرف المورد
    
    Returns:
        Dict: {success: bool, message: str}
    """
    # التحقق من الصلاحية
    if not supplier_product.verify_access(qid, supplier_id):
        return {
            'success': False,
            'message': 'غير مصرح بحذف هذا المنتج'
        }
    
    # حذف المنتج
    from apps.services.product_sync_service import ProductSyncService
    sync = ProductSyncService()
    success = sync.delete_product(qid, delete_mapping=True)
    
    if success:
        return {
            'success': True,
            'message': 'تم حذف المنتج بنجاح'
        }
    
    return {
        'success': False,
        'message': 'فشل حذف المنتج'
    }


def bulk_delete_products(qids: List[str], supplier_id: int) -> Dict:
    """
    حذف منتجات متعددة مع التحقق من الصلاحية
    
    Args:
        qids: قائمة معرفات المنتجات
        supplier_id: معرف المورد
    
    Returns:
        Dict: {success: bool, message: str, deleted: int, failed: int}
    """
    deleted = 0
    failed = 0
    errors = []
    
    for qid in qids:
        result = delete_product(qid, supplier_id)
        if result.get('success'):
            deleted += 1
        else:
            failed += 1
            errors.append({'qid': qid, 'error': result.get('message')})
    
    return {
        'success': failed == 0,
        'message': f'تم حذف {deleted} منتج' if failed == 0 else f'تم حذف {deleted} منتج وفشل {failed}',
        'deleted': deleted,
        'failed': failed,
        'errors': errors
    }


# ============================================================
# 📦 BULK OPERATIONS - عمليات دفعة واحدة
# ============================================================

def bulk_update_status(qids: List[str], supplier_id: int, status: str) -> Dict:
    """
    تحديث حالة منتجات متعددة
    
    Args:
        qids: قائمة معرفات المنتجات
        supplier_id: معرف المورد
        status: الحالة الجديدة
    
    Returns:
        Dict: {success: bool, updated: int, failed: int}
    """
    updated = 0
    failed = 0
    
    for qid in qids:
        # التحقق من الصلاحية
        if not supplier_product.verify_access(qid, supplier_id):
            failed += 1
            continue
        
        # تحديث الحالة
        result = supplier_product.update_product_status(qid, supplier_id, status)
        if result.get('success'):
            updated += 1
        else:
            failed += 1
    
    return {
        'success': failed == 0,
        'updated': updated,
        'failed': failed,
        'message': f'تم تحديث {updated} منتج' if failed == 0 else f'تم تحديث {updated} منتج وفشل {failed}'
    }


# ============================================================
# 📋 EXPORTS
# ============================================================

__all__ = [
    'get_products',
    'get_product_stats',
    'get_suppliers_list',
    'get_supplier_info',
    'get_product_by_qid',
    'get_product_with_mapping',
    'filter_products',
    'search_products',
    'paginate_products',
    'delete_product',
    'bulk_delete_products',
    'bulk_update_status'
]
