# coding: utf-8
# 📂 apps/auth_portal/registry.py

from .routes import auth_portal

# تعريفات الموديول (حتى لو لم تظهر في القائمة، يفضل تعريفها للنظام)
MODULE_NAME = "بوابة الوصول"
MODULE_ICON = "fas fa-shield-alt"
LINKS = {} # فارغ لأنها صفحة تسجيل دخول ولا تحتاج للظهور في القائمة الجانبية

def register_module(app):
    """
    دالة التسجيل الديناميكي: 
    يتم استدعاؤها من قبل المصنع (Factory) لاكتشاف وتسجيل 
    الـ Blueprints الخاصة بموديول البوابة.
    """
    # تسجيل الـ Blueprint الخاص بالبوابة
    app.register_blueprint(auth_portal, url_prefix='/auth')
    
    # يمكنك إضافة أي تهيئة إضافية خاصة بهذا الموديول هنا
