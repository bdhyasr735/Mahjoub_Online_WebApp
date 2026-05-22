# coding: utf-8
from flask import Flask
from apps.extensions import db, login_manager
from config import Config

def create_app():
    # 1. إنشاء التطبيق
    app = Flask(__name__)
    app.config.from_object(Config)

    # 2. تهيئة الإضافات
    db.init_app(app)
    login_manager.init_app(app)
    
    # تحديد مسار صفحة الدخول التلقائي
    login_manager.login_view = 'auth_portal.login' 

    # 3. دالة تعريف المستخدم (تم تحريك الاستيراد لداخل الدالة لتجنب أخطاء الدورة)
    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # 4. تسجيل الـ Blueprints (النوافذ المستقلة)
    # ملاحظة: يتم الاستيراد هنا لتجنب مشاكل الاستيراد الدائري
    
    from apps.auth_portal import auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from apps.admin_dashboard import admin_dashboard_bp
    app.register_blueprint(admin_dashboard_bp, url_prefix='/admin')
    
    from apps.add_supplier import admin_suppliers_bp
    app.register_blueprint(admin_suppliers_bp, url_prefix='/suppliers')
    
    from apps.wallet import wallet_bp
    app.register_blueprint(wallet_bp, url_prefix='/wallet')

    return app
