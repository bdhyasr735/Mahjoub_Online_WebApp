# coding: utf-8
# 📂 apps/suppliers_product/registry.py

import logging
from flask import url_for, session

logger = logging.getLogger(__name__)

MODULE_NAME = "منتجات المورد"
MODULE_ICON = "fa-boxes"
SHOW_IN_SUPPLIER = True

LINKS = {
    "suppliers_product_bp.manage_supplier_products_view": "📦 منتجاتي",
    "suppliers_product_bp.add_supplier_product": "➕ إضافة منتج جديد",
    "suppliers_product_bp.review_supplier_products": "📋 مراجعة الحالات"
}


def register_module(app):
    """تسجيل موديول منتجات الموردين في التطبيق"""
    try:
        from apps.suppliers_product.routes import suppliers_product_bp
        if 'suppliers_product_bp' not in app.blueprints:
            app.register_blueprint(suppliers_product_bp, url_prefix='/supplier')
            print("✅ [Registry Supplier]: تم تسجيل موديول منتجات الموردين.")
        else:
            print("ℹ️ [Registry Supplier]: موديول منتجات الموردين مسجل مسبقاً.")
    except ImportError as e:
        print(f"❌ [Registry Supplier]: خطأ في استيراد routes: {e}")
    except Exception as e:
        print(f"❌ [Registry Supplier]: خطأ في تسجيل suppliers_product: {e}")
    return app


def get_module_stats():
    """جلب إحصائيات منتجات المورد الحالي"""
    try:
        from apps.services import services
        from apps.models.product_supplier_map import ProductSupplierMapping

        supplier_id = session.get('user_id') or session.get('supplier_id')
        user_type = session.get('user_type')

        result = services.products.get_all_products() or {}
        all_products = result.get('data', [])

        if user_type != 'admin' and supplier_id:
            supplier_mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
            supplier_qids = {m.product_qid for m in supplier_mappings}
            products = [p for p in all_products if p.get('qid') in supplier_qids]
        else:
            products = all_products
        
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
        print(f"❌ [Registry Supplier Stats Error]: {e}")
        return {
            'total': 0, 
            'active': 0, 
            'draft': 0, 
            'archived': 0, 
            'has_products': False
        }


def get_module_link():
    """الحصول على رابط موديول الموردين"""
    try:
        return url_for('suppliers_product_bp.manage_supplier_products_view')
    except Exception as e:
        print(f"❌ [Registry Supplier Link Error]: {e}")
        return '#'


def get_dashboard_card():
    """الحصول على بطاقة موديول الموردين لوحة التحكم"""
    stats = get_module_stats()
    return {
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'link': get_module_link(),
        'stats': stats,
        'color': 'green',
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
