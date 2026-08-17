# coding: utf-8
# 📂 apps/admin_suppliers_wallets/__init__.py
"""
حزمة إدارة محافظ الموردين وطلبات السحب
Mahjoub Online WebApp
"""

from flask import Blueprint

def create_admin_suppliers_wallets_blueprint():
    """
    إنشاء وإعداد Blueprint لموديول محافظ الموردين
    مع تسجيل جميع المسارات الفرعية
    """
    # إنشاء الـ Blueprint الرئيسي
    bp = Blueprint(
        'admin_suppliers_wallets',
        __name__,
        template_folder='templates',
        static_folder='static',
        url_prefix='/admin/suppliers-wallets'
    )

    # ✅ تسجيل مسارات المحافظ (القائمة، التفاصيل، ...)
    from apps.admin_suppliers_wallets.routes import suppliers_wallets_controller
    bp.register_blueprint(suppliers_wallets_controller.bp)

    # ✅ تسجيل مسارات طلبات السحب
    from apps.admin_suppliers_wallets.routes import withdraw_requests_controller
    bp.register_blueprint(withdraw_requests_controller.bp)

    print(f"🔧 [Blueprint]: تم إنشاء Blueprint '{bp.name}' مع {len(bp.deferred_functions)} مسار مسجل.")
    return bp


# للاستيراد المباشر في حالة عدم استخدام create function
# (احتياطي للتوافق مع أنظمة التسجيل المختلفة)
blueprint = create_admin_suppliers_wallets_blueprint()
