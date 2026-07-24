# coding: utf-8
# 📂 apps/admin_Product/registry.py

MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fa-boxes"
SHOW_IN_SUPPLIER = False

# ✅ الروابط الأساسية
LINKS = {
    "admin_product_bp.manage_products": "📦 إدارة المنتجات",
    "admin_product_bp.add_product": "➕ إضافة منتج",
    "admin_product_bp.review_products": "📋 مراجعة المنتجات"
}


def register_module(app):
    """تسجيل موديول إدارة المنتجات في لوحة التحكم"""
    try:
        # ✅ استيراد داخل الدالة يكسر دائرة الاستيراد
        from apps.admin_Product.routes import admin_product_bp
        
        # ✅ تسجيل Blueprint المنتجات
        if 'admin_product_bp' not in app.blueprints:
            app.register_blueprint(admin_product_bp, url_prefix='/admin')
            print("✅ [Registry]: تم تسجيل موديول إدارة المنتجات بنجاح.")
        else:
            print("ℹ️ [Registry]: admin_product_bp مسجل مسبقاً")
            
    except ImportError as e:
        print(f"❌ [Registry]: خطأ في استيراد admin_product: {e}")
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل admin_product: {e}")
    
    return app


def get_module_stats():
    """جلب إحصائيات المنتجات (للوحة التحكم)"""
    try:
        from apps.services.product_sync_service import ProductSyncService
        sync_service = ProductSyncService()
        products = sync_service.fetch_products(page=1, limit=1)
        
        total = products.get('pagination', {}).get('total', 0)
        
        return {
            'total': total,
            'active': 0,
            'draft': 0,
            'pending': 0,
            'has_products': total > 0
        }
    except Exception as e:
        print(f"❌ خطأ في get_module_stats: {e}")
        return {
            'total': 0,
            'active': 0,
            'draft': 0,
            'pending': 0,
            'has_products': False
        }


def get_module_link():
    """الحصول على رابط الموديول"""
    from flask import url_for
    return url_for('admin_product_bp.manage_products')


def get_dashboard_card():
    """الحصول على بيانات البطاقة للوحة التحكم"""
    stats = get_module_stats()
    
    return {
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'link': get_module_link(),
        'stats': stats,
        'color': 'blue',
        'badge': stats.get('total', 0),
        'subtitle': f"{stats.get('active', 0)} نشط، {stats.get('draft', 0)} مسودة"
    }


# ============================================================
# ✅ تصدير الدوال الأساسية
# ============================================================

__all__ = [
    'MODULE_NAME',
    'MODULE_ICON',
    'SHOW_IN_SUPPLIER',
    'LINKS',
    'register_module',
    'get_module_stats',
    'get_module_link',
    'get_dashboard_card'
]
