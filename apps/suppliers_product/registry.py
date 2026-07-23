# coding: utf-8
# 📂 apps/suppliers_product/registry.py

"""
تسجيل تطبيق منتجات الموردين في المنصة
"""

from flask import Blueprint, url_for

# ✅ بيانات الموديول
MODULE_NAME = "منتجاتي"
MODULE_ICON = "fas fa-boxes"
SHOW_IN_SUPPLIER = True

# ✅ الروابط - تأكد من أن الاسم صحيح
LINKS = {
    'suppliers_product_bp.products': '📦 منتجاتي'
}

# ✅ تعريف الـ Blueprint (تم نقله إلى هنا)
suppliers_product_bp = Blueprint(
    'suppliers_product_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/suppliers_product/static'
)


def register_module(app):
    """تسجيل الموديول في التطبيق"""
    # ✅ استيراد الـ routes بعد تعريف الـ Blueprint
    from apps.suppliers_product import routes
    
    if 'suppliers_product_bp' not in app.blueprints:
        app.register_blueprint(suppliers_product_bp, url_prefix='/supplier')
        print("✅ [Registry]: تم تسجيل 'suppliers_product' بنجاح.")
    return app


# ============================================================
# ✅ دالة للحصول على إحصائيات المنتجات للمورد
# ============================================================
def get_module_stats(supplier_id):
    """
    جلب إحصائيات منتجات المورد لعرضها في لوحة التحكم
    
    Args:
        supplier_id: معرف المورد
        
    Returns:
        dict: إحصائيات المنتجات
    """
    from apps.models.product_supplier_map import ProductSupplierMapping
    from apps.services.product_sync_service import ProductSyncService
    import os
    
    try:
        # جلب جميع المنتجات المرتبطة بالمورد
        mappings = ProductSupplierMapping.query.filter_by(
            supplier_id=supplier_id,
            status='active'
        ).all()
        
        product_qids = [m.product_qid for m in mappings]
        total_products = len(product_qids)
        
        # جلب بيانات المنتجات من Qumra (للحصول على الحالات)
        token = os.environ.get('QUMRA_API_KEY', '')
        sync_service = ProductSyncService(token=token)
        
        published = 0
        draft = 0
        rejected = 0
        archived = 0
        
        for qid in product_qids:
            product = sync_service.fetch_product_by_qid(qid)
            if product:
                status = product.get('status', '').upper()
                if status == 'PUBLISHED':
                    published += 1
                elif status == 'DRAFT':
                    draft += 1
                elif status == 'REJECTED':
                    rejected += 1
                elif status == 'ARCHIVED':
                    archived += 1
        
        return {
            'total': total_products,
            'published': published,
            'draft': draft,
            'rejected': rejected,
            'archived': archived,
            'has_products': total_products > 0
        }
        
    except Exception as e:
        print(f"❌ خطأ في get_module_stats: {e}")
        return {
            'total': 0,
            'published': 0,
            'draft': 0,
            'rejected': 0,
            'archived': 0,
            'has_products': False
        }


# ============================================================
# ✅ دالة للحصول على رابط الموديول
# ============================================================
def get_module_link():
    """الحصول على رابط صفحة المنتجات"""
    return url_for('suppliers_product_bp.products')


# ============================================================
# ✅ دالة للحصول على بيانات الموديول للعرض في لوحة التحكم
# ============================================================
def get_dashboard_card(supplier_id):
    """
    الحصول على بيانات بطاقة الموديول لعرضها في لوحة التحكم
    
    Args:
        supplier_id: معرف المورد
        
    Returns:
        dict: بيانات البطاقة
    """
    stats = get_module_stats(supplier_id)
    
    return {
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'link': get_module_link(),
        'stats': stats,
        'color': 'purple',
        'badge': stats['total'],
        'subtitle': f"{stats['published']} منشور، {stats['draft']} قيد المراجعة"
    }
