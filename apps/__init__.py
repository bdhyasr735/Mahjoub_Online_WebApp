# coding: utf-8
from flask import Flask
from apps.extensions import db, login_manager
from config import Config

def create_app():
    """
    دالة المصنع (Application Factory) لإنشاء تطبيق Flask وتأمين بواباته.
    """
    # 1. إنشاء التطبيق وشحن الإعدادات
    app = Flask(__name__)
    app.config.from_object(Config)

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

    # 4. تسجيل الـ Blueprints (السيادة الرقمية المستقلة)
    # يتم الاستيراد محلياً داخل الدالة لتجنب مشاكل الاستيراد الدائري (Circular Imports)
    
    # بوابة التحكم بالدخول والسيادة الجمركية للمنصة
    from apps.auth_portal import auth_blueprint
    # تأكدنا أن الاسم البرمجي الداخلي للـ Blueprint في ملف الـ routes الخاص به هو 'auth_portal'
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    # لوحة القيادة المركزية والرقابة الفورية لـ "محجوب أونلاين"
    from apps.admin_dashboard import admin_dashboard
    # تعديل الاسم المتغير ليتطابق مع الاستدعاء الموحد 'admin_dashboard.dashboard'
    app.register_blueprint(admin_dashboard, url_prefix='/admin')
    
    # حوكمة وإدارة الموردين (شركاء النجاح)
    from apps.add_supplier import admin_suppliers_bp
    app.register_blueprint(admin_suppliers_bp, url_prefix='/suppliers')
    
    # النظام المالي والربط البرمجي للمحفظة الرقمية
    from apps.wallet import wallet_bp
    app.register_blueprint(wallet_bp, url_prefix='/wallet')

    return app
