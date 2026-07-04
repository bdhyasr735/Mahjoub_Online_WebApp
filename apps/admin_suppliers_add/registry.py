# coding: utf-8
from .routes import admin_suppliers_add_bp

# لا تضع MODULE_NAME هنا إذا كنت تريد دمجهما في القائمة الجانبية 
# (ملاحظة: هذا النظام لا يدمج الأسماء تلقائياً، لذا سيظهران كعنصرين منفصلين، وهذا أضمن وأكثر استقراراً)

def register_module(app):
    try:
        app.register_blueprint(admin_suppliers_add_bp, url_prefix='/admin/suppliers_add')
        print("✅ [Registry]: تم تسجيل موديول 'admin_suppliers_add' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'admin_suppliers_add': {e}")
