# coding: utf-8
# 📂 apps/suppliers_product/registry.py

"""
تسجيل تطبيق إدارة منتجات المورد في المنصة مع القائمة المنسدلة الاحترافية
"""

import logging
from flask import Flask

logger = logging.getLogger(__name__)

# ============================================
# معلومات الموديول
# ============================================

MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fas fa-box"
MODULE_DESCRIPTION = "إدارة منتجات الموردين بسهولة"
SHOW_IN_SUPPLIER = True
SHOW_IN_ADMIN = False
ORDER = 10  # ترتيب الظهور في القائمة

# ============================================
# روابط القائمة الجانبية
# ============================================

LINKS = {
    'suppliers_product_bp.products': {
        'title': '📦 قائمة المنتجات',
        'icon': 'fas fa-list',
        'description': 'عرض وإدارة جميع المنتجات'
    },
    'add_product_bp.add_product_page': {
        'title': '➕ إضافة منتج جديد',
        'icon': 'fas fa-plus-circle',
        'description': 'إضافة منتج جديد للمورد'
    }
}

# ============================================
# صلاحيات الموديول (Permissions)
# ============================================

PERMISSIONS = {
    'view_products': 'عرض المنتجات',
    'add_product': 'إضافة منتج',
    'edit_product': 'تعديل المنتج',
    'delete_product': 'حذف المنتج',
    'manage_inventory': 'إدارة المخزون'
}

# ============================================
# إعدادات الموديول
# ============================================

SETTINGS = {
    'enable_auto_sku': True,
    'enable_bulk_upload': False,
    'max_images_per_product': 10,
    'enable_variants': True,
    'default_status': 'DRAFT'
}

# ============================================
# دالة التسجيل
# ============================================

def register_module(app: Flask) -> Flask:
    """
    تسجيل تطبيق منتجات المورد والـ Blueprints الخاصة به
    
    Args:
        app: تطبيق Flask
        
    Returns:
        Flask: التطبيق بعد التسجيل
    """
    try:
        from apps.suppliers_product.routes import bp, add_bp, edit_bp
        
        # تسجيل الـ Blueprints
        blueprints = [
            (bp, 'suppliers_product_bp', '/supplier'),
            (add_bp, 'add_product_bp', '/supplier'),
            (edit_bp, 'edit_product_bp', '/supplier')
        ]
        
        for blueprint, name, prefix in blueprints:
            if name not in app.blueprints:
                app.register_blueprint(blueprint, url_prefix=prefix)
                logger.info(f"✅ [Registry]: تم تسجيل {name}")
            else:
                logger.warning(f"⚠️ [Registry]: {name} مسجل مسبقاً")
        
        # تسجيل الـ Context Processor (اختياري)
        @app.context_processor
        def inject_product_module():
            return {
                'product_module': {
                    'name': MODULE_NAME,
                    'icon': MODULE_ICON,
                    'links': LINKS,
                    'settings': SETTINGS
                }
            }
        
        logger.info(f"✅ [Registry]: تم تسجيل موديول {MODULE_NAME} بنجاح")
        
    except ImportError as e:
        logger.error(f"❌ [Registry]: فشل استيراد الموديول - {e}")
    except Exception as e:
        logger.error(f"❌ [Registry]: خطأ في تسجيل موديول suppliers_product: {e}")
    
    return app


# ============================================
# دالة للحصول على روابط الموديول
# ============================================

def get_module_links() -> dict:
    """الحصول على روابط الموديول للقائمة الجانبية"""
    return {
        'name': MODULE_NAME,
        'icon': MODULE_ICON,
        'links': [
            {
                'endpoint': endpoint,
                'title': info['title'] if isinstance(info, dict) else info,
                'icon': info.get('icon', 'fas fa-circle') if isinstance(info, dict) else None,
                'description': info.get('description', '') if isinstance(info, dict) else ''
            }
            for endpoint, info in LINKS.items()
        ]
    }


# ============================================
# دالة للتحقق من الصلاحيات
# ============================================

def has_permission(user, permission: str) -> bool:
    """
    التحقق من صلاحية المستخدم
    
    Args:
        user: كائن المستخدم
        permission: اسم الصلاحية
        
    Returns:
        bool: هل لديه الصلاحية
    """
    if not user:
        return False
    
    # المستخدمين من نوع staff أو admin لديهم جميع الصلاحيات
    if hasattr(user, 'user_type') and user.user_type in ['staff', 'admin']:
        return True
    
    # التحقق من الصلاحية المحددة
    if hasattr(user, 'permissions'):
        return permission in user.permissions
    
    return False
