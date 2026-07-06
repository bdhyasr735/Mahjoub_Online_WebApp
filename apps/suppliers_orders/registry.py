from apps.suppliers_orders.routes import suppliers_orders_bp

MODULE_NAME = "الطلبات"
MODULE_ICON = "fa-shopping-cart"

# هنا نستخدم المفتاح 'orders' ليطابق القائمة البيضاء في admin_base.html
# ونربطه بـ الـ endpoint الفعلي 'suppliers_orders.dashboard'
LINKS = {
    "قائمة الطلبات": "suppliers_orders.dashboard"
}

def register_module(app):
    try:
        # تسجيل الـ Blueprint باسمه الحالي
        app.register_blueprint(suppliers_orders_bp, url_prefix='/suppliers_orders')
        
        # إضافة الموديول إلى القائمة التي يقرؤها admin_base.html
        # لاحظ أننا استخدمنا المفتاح 'orders' ليتوافق مع القائمة البيضاء
        if not hasattr(app, 'registered_modules'):
            app.registered_modules = {}
            
        app.registered_modules['orders'] = {
            'display_name': MODULE_NAME,
            'icon': MODULE_ICON,
            'links': LINKS
        }
        print("✅ [Registry]: تم تسجيل موديول 'suppliers_orders' تحت مفتاح 'orders' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'Orders': {e}")
