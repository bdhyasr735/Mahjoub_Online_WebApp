# coding: utf-8
# 📂 apps/admin_Product/registry.py

import logging
from flask import url_for

logger = logging.getLogger(__name__)

MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fa-boxes"
SHOW_IN_SUPPLIER = False

LINKS = {
    "admin_product_bp.manage_products": "📦 إدارة المنتجات",
    "admin_product_bp.add_product": "➕ إضافة منتج",
    "admin_product_bp.review_products": "📋 مراجعة المنتجات"
}


def register_module(app):
    """تسجيل موديول إدارة المنتجات في التطبيق"""
    try:
        from apps.admin_Product.routes import admin_product_bp
        if 'admin_product_bp' not in app.blueprints:
            app.register_blueprint(admin_product_bp, url_prefix='/admin')
            print("✅ [Registry]: تم تسجيل موديول إدارة المنتجات.")
        else:
            print("ℹ️ [Registry]: موديول إدارة المنتجات مسجل مسبقاً.")
    except ImportError as e:
        print(f"❌ [Registry]: خطأ في استيراد routes: {e}")
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل admin_product: {e}")
    return app


def get_module_stats():
    """جلب إحصائيات المنتجات"""
    try:
        from apps.services import services
        products = services.products.get_all_products() or []
        
        stats = {
            'total': len(products), 
            'active': 0, 
            'draft': 0, 
            'archived': 0,
            'has_products': len(products) > 0
        }
        
        for p in products:
            status = p.get('status', '').upper()
            is_active = p.get('isActive', False)
            
            if status in ['ACTIVE', 'PUBLISHED'] or is_active:
                stats['active'] += 1
            elif status == 'DRAFT':
                stats['draft'] += 1
            elif status == 'ARCHIVED':
                stats['archived'] += 1
                
        return stats
    except Exception as e:
        print(f"❌ [Registry Stats Error]: {e}")
        return {
            'total': 0, 
            'active': 0, 
            'draft': 0, 
            'archived': 0, 
            'has_products': False
        }


def get_module_link():
    """الحصول على رابط الموديول"""
    try:
        return url_for('admin_product_bp.manage_products')
    except Exception as e:
        print(f"❌ [Registry Link Error]: {e}")
        return '#'


def get_dashboard_card():
    """الحصول على بطاقة الموديول للوحة التحكم"""
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
