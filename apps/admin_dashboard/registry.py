# coding: utf-8
# 📂 apps/admin_dashboard/registry.py

from .routes import admin_dashboard

def register_module(app):
    """
    تسجيل موديول لوحة تحكم المسؤول (admin_dashboard).
    يتم استدعاء هذه الدالة ديناميكياً بواسطة المصنع (apps/__init__.py).
    """
    # تسجيل البلوبرينت
    app.register_blueprint(admin_dashboard, url_prefix='/admin')
    
    # رسالة تأكيد للـ Logs
    print(f"✅ [Registry]: تم تسجيل موديول 'admin_dashboard' بنجاح على المسار (/admin).")
