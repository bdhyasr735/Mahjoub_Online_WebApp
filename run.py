import os
from flask import Flask
from flask_login import LoginManager
# استيراد المكونات من المجلدات الخاصة بك
from admin_panel.models import db, User
from admin_panel.admin_routes import admin_bp

def create_app():
    app = Flask(__name__)

    # 1. إعدادات الأمان وقاعدة البيانات
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mahjoub_online_sovereign_key_2026')
    
    # جلب الرابط من متغيرات البيئة (Railway) أو استخدام الرابط الذي زودتني به كاحتياط
    raw_uri = os.environ.get('DATABASE_URL', "postgresql://mahjoub_online_1_db_user:S7dxtVGcKwrsM1QEzGOuPPcRL8dKxgXk@dpg-d79tuthr0fns73epej4g-a/mahjoub_online_1_db")
    
    # تصحيح البروتوكول فوراً لضمان عدم تعطل Postgres
    if raw_uri.startswith("postgres://"):
        raw_uri = raw_uri.replace("postgres://", "postgresql://", 1)
        
    app.config['SQLALCHEMY_DATABASE_URI'] = raw_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 2. ربط قاعدة البيانات بالتطبيق
    db.init_app(app)

    # 3. إعداد نظام إدارة الدخول
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login' 

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 4. تسجيل الـ Blueprint (المسارات)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # 5. تهيئة الجداول عند التشغيل
    with app.app_context():
        try:
            db.create_all()
            admin_user = User.query.filter_by(username='علي محجوب').first()
            if not admin_user:
                new_admin = User(username='علي محجوب', role='SuperAdmin')
                new_admin.set_password('123456') 
                db.session.add(new_admin)
                db.session.commit()
                print("✅ حساب القائد جاهز.")
        except Exception as e:
            print(f"❌ خطأ قاعدة البيانات: {str(e)}")

    return app

# هذا السطر هو الأهم لعمل Gunicorn
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
