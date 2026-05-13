from flask import Flask, redirect, url_for
import os
# استيراد القاعدة والموديل السيادي من المجلد الرئيسي
from models.admin_db import db, AdminUser

def create_app():
    # تعديل Flask ليتعرف على مجلد القوالب المركزي المشترك
    app = Flask(__name__, template_folder='apps/templates')
    
    # مفتاح الأمان السيادي للمنصة
    app.secret_key = os.environ.get('SECRET_KEY') or 'MAHJOUB_SECURE_2026'

    # إعداد قاعدة البيانات وتوافق postgres مع Railway
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///mahjoub_admin.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ربط قاعدة البيانات بالتطبيق
    db.init_app(app)

    # تسجيل البوابات الرقمية (التطبيقات المستقلة)
    from apps.auth_portal.routes import auth_bp
    from apps.admin_dashboard import admin_dashboard  
    from apps.add_supplier.routes import admin_suppliers

    # تفعيل المسارات في هيكل النظام
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_dashboard, url_prefix='/admin')
    app.register_blueprint(admin_suppliers, url_prefix='/admin/suppliers')

    # إنشاء الجداول السيادية إذا لم تكن موجودة عند الإقلاع
    with app.app_context():
        db.create_all()

    # التوجيه التلقائي لبوابة الدخول عند فتح الرابط الرئيسي
    @app.route('/')
    def root():
        return redirect(url_for('auth_portal.login')) 

    return app

# إنشاء نسخة التطبيق لمحرك Gunicorn في بيئة Railway
app = create_app()

if __name__ == '__main__':
    # التشغيل على المنفذ المخصص من Railway أو المنفذ الافتراضي 8080
    port = int(os.environ.get('PORT', 8080))
    # الإقلاع بوضع الاستماع العام لضمان ظهور الموقع أونلاين
    app.run(host='0.0.0.0', port=port)
