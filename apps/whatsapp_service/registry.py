# 📂 apps/whatsapp/registry.py

MODULE_NAME = "إدارة الواتساب"
MODULE_ICON = "fa-brands fa-whatsapp"  # أيقونة الموديول
SHOW_IN_SUPPLIER = False               # للعرض في لوحة الإدارة فقط

NAV_ITEMS = [
    {
        "endpoint": "whatsapp.index",   # اسم الـ endpoint الخاص بالبلوبرينت
        "title": "إعدادات الواتساب"
    }
]

def register_module(app):
    from apps.whatsapp.routes import whatsapp_bp
    app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
