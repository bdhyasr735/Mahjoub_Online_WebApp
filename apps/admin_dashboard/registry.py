# 📂 apps/admin_dashboard/registry.py

# الاستيراد الصحيح للـ Blueprint المحدث
from .routes import admin_dashboard_bp 

MODULE_NAME = "لوحة التحكم"
MODULE_ICON = "fas fa-tachometer-alt"

# تم تحديث الرابط ليتناسب مع الاسم الجديد للـ Blueprint
LINKS = {
    "admin_dashboard_bp.dashboard": "الإحصائيات"
}

def register_module(app):
    try:
        # تسجيل الـ Blueprint بـ url_prefix '/admin' كما هو مطلوب
        app.register_blueprint(admin_dashboard_bp, url_prefix='/admin')
        print("✅ [Registry]: تم تسجيل موديول 'admin_dashboard_bp' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول الإحصائيات: {e}")
