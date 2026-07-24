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

# ✅ تعريف الـ Blueprint
suppliers_product_bp = Blueprint(
    'suppliers_product_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/suppliers_product/static'
)

# ✅ الروابط
LINKS = {
    'suppliers_product_bp.products': '📦 منتجاتي'
}


def register_module(app):
    """تسجيل الموديول في التطبيق"""
    try:
        from apps.suppliers_product.suppliers_product_routes import suppliers_product_bp as bp
        from apps.suppliers_product.add_product_routes import add_product_bp
        from apps.suppliers_product.edit_product_routes import edit_product_bp
        
        # ✅ التحقق من وجود الـ Blueprint قبل التسجيل
        if 'suppliers_product_bp' not in app.blueprints:
            app.register_blueprint(bp, url_prefix='/supplier')
            print("✅ [Registry]: تم تسجيل 'suppliers_product_bp'")
        else:
            print("ℹ️ [Registry]: 'suppliers_product_bp' مسجل مسبقاً")
        
        if 'add_product_bp' not in app.blueprints:
            app.register_blueprint(add_product_bp, url_prefix='/supplier')
            print("✅ [Registry]: تم تسجيل 'add_product_bp'")
        else:
            print("ℹ️ [Registry]: 'add_product_bp' مسجل مسبقاً")
        
        if 'edit_product_bp' not in app.blueprints:
            app.register_blueprint(edit_product_bp, url_prefix='/supplier')
            print("✅ [Registry]: تم تسجيل 'edit_product_bp'")
        else:
            print("ℹ️ [Registry]: 'edit_product_bp' مسجل مسبقاً")
            
    except ImportError as e:
        print(f"❌ [Registry]: خطأ في استيراد: {e}")
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل: {e}")
    
    return app


# ============================================================
# ✅ دالة للحصول على إحصائيات المنتجات للمورد
# ============================================================

def get_module_stats(supplier_id):
    """
    جلب إحصائيات منتجات المورد
    
    Args:
        supplier_id: معرف المورد
    
    Returns:
        dict: {
            'total': int,
            'published': int,
            'draft': int,
            'rejected': int,
            'archived': int,
            'has_products': bool
        }
    """
    from apps.models.product_supplier_map import ProductSupplierMapping
    from apps.suppliers_product.services.product_sync_service import supplier_product
    
    try:
        # جلب العلاقات من الخدمة
        mappings = supplier_product.get_supplier_mappings(supplier_id)
        
        if not mappings:
            return {
                'total': 0,
                'published': 0,
                'draft': 0,
                'rejected': 0,
                'archived': 0,
                'has_products': False
            }
        
        total_products = len(mappings)
        published = 0
        draft = 0
        rejected = 0
        archived = 0
        
        # جلب بيانات كل منتج من قمرة
        for mapping in mappings:
            qid = mapping.get('qid')
            product = supplier_product.fetch_product_by_qid(qid)
            if product:
                status = product.get('status', '').upper()
                if status in ['PUBLISHED', 'ACTIVE']:
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
    """الحصول على رابط الصفحة الرئيسية للموديول"""
    return url_for('suppliers_product_bp.products')


# ============================================================
# ✅ دالة للحصول على بيانات الموديول للعرض في لوحة التحكم
# ============================================================

def get_dashboard_card(supplier_id):
    """
    الحصول على بيانات البطاقة لعرضها في لوحة التحكم
    
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


# ============================================================
# ✅ دالة للحصول على قائمة منتجات المورد (للاستخدام السريع)
# ============================================================

def get_supplier_products(supplier_id):
    """
    جلب قائمة منتجات المورد مع بياناتها
    
    Args:
        supplier_id: معرف المورد
    
    Returns:
        list: قائمة المنتجات
    """
    from apps.suppliers_product.services.product_sync_service import supplier_product
    
    try:
        # جلب العلاقات
        mappings = supplier_product.get_supplier_mappings(supplier_id)
        
        products = []
        for mapping in mappings:
            qid = mapping.get('qid')
            product = supplier_product.fetch_product_by_qid(qid)
            if product:
                products.append({
                    'qid': qid,
                    'title': product.get('title'),
                    'price': product.get('price'),
                    'status': product.get('status'),
                    'created_at': mapping.get('created_at'),
                    'mapping_id': mapping.get('id')
                })
        
        return products
        
    except Exception as e:
        print(f"❌ خطأ في get_supplier_products: {e}")
        return []


# ============================================================
# ✅ تصدير الدوال الأساسية
# ============================================================

__all__ = [
    'MODULE_NAME',
    'MODULE_ICON',
    'SHOW_IN_SUPPLIER',
    'LINKS',
    'suppliers_product_bp',
    'register_module',
    'get_module_stats',
    'get_module_link',
    'get_dashboard_card',
    'get_supplier_products'
]
