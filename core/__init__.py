import os
from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# 1. تعريف الكائنات الأساسية
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # 2. جلب الإعدادات من ملف Config السيادي
    # تأكد أن ملف config.py موجود في المجلد الرئيسي بجانب run.py
    from config import Config
    app.config.from_object(Config)

    # 3. تهيئة الإضافات
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # تحديد الصفحة التي يتم التوجه إليها عند الحاجة لتسجيل الدخول
    login_manager.login_view = 'admin_panel.admin_login'

    # 4. نظام التوجيه الذكي (بدل رسالة unauthorized السوداء)
    @login_manager.unauthorized_handler
    def unauthorized():
        # إذا حاول أي شخص الدخول لصفحة محمية بدون تسجيل، يذهب فوراً لصفحة الدخول
        return redirect(url_for('admin_panel.admin_login'))

    with app.app_context():
        # استيراد النماذج (Models) لربطها بقاعدة البيانات
        from core import models
        
        # 5. تسجيل البوابات (Blueprints)
        # تسجيل بوابة الموردين
        try:
            from supplier_panel import supplier_bp
            app.register_blueprint(supplier_bp, url_prefix='/supplier')
            print("✅ تم تفعيل بوابة الموردين")
        except Exception as e:
            print(f"⚠️ بوابة الموردين غير متوفرة حالياً: {e}")

        # تسجيل بوابة الإدارة (الباب السري)
        try:
            from admin_panel import admin_bp 
            app.register_blueprint(admin_bp, url_prefix='/admin_control_9046')
            print("✅ تم تفعيل بوابة الإدارة بنجاح")
        except Exception as e:
            print(f"⚠️ فشل تسجيل بوابة الإدارة: {e}")

        # إنشاء الجداول تلقائياً إذا لم تكن موجودة
        db.create_all()

    return app

# ملاحظة: تم حذف سطر app = create_app() من هنا لمنع التضارب مع ملف run.py

@login_manager.user_loader
def load_user(user_id):
    from core.models import User
    try:
        return User.query.get(int(user_id))
    except:
        return None
