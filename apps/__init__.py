# coding: utf-8
from flask import Flask
from apps.extensions import db, login_manager
from config import Config
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    """
    دالة المصنع (Application Factory) لإنشاء تطبيق Flask وتأمين بواباته.
    """
    # 1. إنشاء التطبيق وشحن الإعدادات
    app = Flask(__name__)
    app.config.from_object(Config)

    # 🚀 معالجة الـ Proxy لبيئات الإنتاج (Railway) لمنع تفكك الجلسة وحلقة التوجيه اللانهائية
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # 2. تهيئة الإضافات المركزية
    db.init_app(app)
    login_manager.init_app(app)
    
    # تحديد مسار صفحة الدخول التلقائي الآمن
    login_manager.login_view = 'auth_portal.login' 

    # 3. دالة تعريف المستخدم (تحميل آمن للمؤسس والمسؤولين)
    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # 4. تسجيل النماذج وتوليد الجداول تلقائياً عند الإقلاع (بديل الترمينال)
    with app.app_context():
        from apps.models import wallet_db  # استدعاء النماذج المالية والسيادية الجديدة
        db.create_all()  # 🔥 هذا الأمر سيقوم بإنشاء الجداول والتحسينات الجديدة فوراً في السيرفر

    # 5. تسجيل الـ Blueprints (السيادة الرقمية المستقلة)
    
    # بوابة التحكم بالدخول والسيادة الجمركية للمنصة
    from apps.auth_portal import auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    # لوحة القيادة المركزية والرقابة الفورية لـ "محجوب أونلاين"
    from apps.admin_dashboard import admin_dashboard
    app.register_blueprint(admin_dashboard, url_prefix='/admin')
    
    # حوكمة وإدارة الموردين (شركاء النجاح)
    from apps.add_supplier import admin_suppliers_bp
    app.register_blueprint(admin_suppliers_bp, url_prefix='/suppliers')
    
    # النظام المالي والربط البرمجي للمحفظة الرقمية
    from apps.wallet import wallet_blueprint
    app.register_blueprint(wallet_blueprint, url_prefix='/wallet')

    return app
