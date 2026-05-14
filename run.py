# coding: utf-8
from flask import Flask, redirect, url_for
import os
# استيراد القاعدة والموديل السيادي من المجلد الرئيسي لضمان وحدة البيانات
from models.admin_db import db, AdminUser
# استيراد دالة التحديث التلقائي للأعمدة الناقصة لجدول الموردين
from models.supplier_db import check_and_upgrade_db

def create_app():
    # تعديل Flask ليتعرف على مجلد القوالب المركزي المشترك وفق هيكلية المشروع
    app = Flask(__name__, template_folder='apps/templates')
    
    # مفتاح الأمان السيادي للمنصة - حماية محجوب أونلاين 2026
    app.secret_key = os.environ.get('SECRET_KEY') or 'MAHJOUB_SECURE_2026'

    # إعداد قاعدة البيانات وتوافق postgres مع بيئة Railway الاحترافية
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///mahjoub_admin.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ربط كائن قاعدة البيانات المركزي بالتطبيق
    db.init_app(app)

    # --- تسجيل البوابات الرقمية (التطبيقات المستقلة كـ Blueprints) ---
    from apps.auth_portal.routes import auth_bp
    from apps.admin_dashboard import admin_dashboard  
    # استيراد تطبيق الموردين الجديد لتعميدهم في النظام
    from apps.add_supplier.routes import admin_suppliers

    # تفعيل المسارات في هيكل النظام مع تحديد بادئات الروابط (URL Prefixes)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_dashboard, url_prefix='/admin')
    # تعيين مسار إدارة الموردين تحت إدارة الإدارة المركزية
    app.register_blueprint(admin_suppliers, url_prefix='/admin/suppliers')

    # إنشاء الجداول السيادية (بما فيها جدول الموردين الجديد) تلقائياً عند الإقلاع
    with app.app_context():
        db.create_all()
        # 🔥 تشغيل الفحص الذكي وتحديث الأعمدة الناقصة في قاعدة بيانات Railway تلقائياً
        check_and_upgrade_db(app)

    # التوجيه التلقائي لبوابة الدخول عند فتح الرابط الرئيسي للمنصة
    @app.route('/')
    def root():
        # ملاحظة: إذا كان اسم الـ Blueprint هو auth_bp، يتم التوجيه لـ auth.login أو حسب الـ endpoint
        try:
            return redirect(url_for('auth_portal.login'))
        except:
            return redirect(url_for('auth.login')) 

    return app

# إنشاء نسخة التطبيق لمحرك Gunicorn في بيئة Railway لضمان استقرار التشغيل
app = create_app()

if __name__ == '__main__':
    # التشغيل على المنفذ المخصص من Railway أو المنفذ الافتراضي 8080
    port = int(os.environ.get('PORT', 8080))
    # الإقلاع بوضع الاستماع العام (0.0.0.0) لضمان ظهور الموقع أونلاين في اليمن والعالم
    app.run(host='0.0.0.0', port=port)
