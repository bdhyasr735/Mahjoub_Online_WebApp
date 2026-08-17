# coding: utf-8
# 📂 apps/admin_treasury/__init__.py
"""
حزمة الرقابة المالية (الخزينة المركزية)
Mahjoub Online WebApp
"""

from flask import Blueprint

# إنشاء الـ Blueprint الرئيسي للخزينة
admin_treasury_bp = Blueprint(
    'admin_treasury',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/admin/treasury'
)

# ✅ استيراد الـ Controller لتسجيل المسارات
from apps.admin_treasury.routes import treasury_controller

# ✅ (اختياري) استيراد مسارات إضافية إن وجدت
# from apps.admin_treasury.routes import reports_controller

print(f"🔧 [Blueprint]: تم إنشاء Blueprint 'admin_treasury' مع المسار {admin_treasury_bp.url_prefix}")


# دالة مساعدة للاستيراد من أنظمة التسجيل المختلفة
def create_admin_treasury_blueprint():
    """إعادة الـ Blueprint نفسه للتوافق مع نظام التسجيل المركزي"""
    return admin_treasury_bp
