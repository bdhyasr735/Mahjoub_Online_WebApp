from flask import Flask, redirect, url_for
import os
from models.admin_db import db, AdminUser  # استدعاء المحرك وموديل المسؤولين

# استيراد البوابات (Blueprints) بناءً على الهيكلية الجديدة
from apps.admin_dashboard.routes import admin_bp
from apps.auth.routes import auth_bp            # تأكد من اسم المجلد 'auth'
from apps.add_supplier.routes import add_supplier_bp

app = Flask(__name__)

# --- إعدادات الحماية والسيادة ---

# المفتاح السري لتشفير الجلسات
app.secret_key = os.environ.get('SECRET_KEY') or 'MAHJOUB_CENTRAL_SECURE_2026_@_PRIVATE'

# إعداد مسار قاعدة البيانات (Postgres للإنتاج و SQLite للتطوير)
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///mahjoub_admin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- ربط المكونات بالمنظومة ---

db.init_app(app)

# تسجيل البوابات بمساراتها الصحيحة
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(add_supplier_bp, url_prefix='/admin') # جعل إضافة المورد تتبع الـ admin

@app.route('/')
def root():
    """ توجيه تلقائي لبوابة الدخول لضمان الهوية """
    return redirect(url_for('auth.login'))

# --- تهيئة المنظومة وإنشاء الحساب القيادي ---

def setup_database():
    with app.app_context():
        # 1. إنشاء الجداول الجديدة (مثل admin_users) في Postgres
        db.create_all()
        
        # 2. التأكد من وجود حساب "علي محجوب" بكلمة السر 123
        check_admin = AdminUser.query.filter_by(username='ali_mahjoub').first()
        if not check_admin:
            # إنشاء حساب المؤسس إذا كان الجدول فارغاً
            founder = AdminUser(
                username='ali_mahjoub',
                full_name='علي محجوب',
                role='founder'
            )
            founder.set_password('123') # تشفير كلمة السر 123
            db.session.add(founder)
            db.session.commit()
            print("🛡️ تم إنشاء حساب المؤسس علي محجوب بنجاح.")

# --- تشغيل المحرك المركزي ---

if __name__ == '__main__':
    setup_database() # تنفيذ تهيئة البيانات
    
    port = int(os.environ.get('PORT', 5000))
    # debug=True مفيد جداً لإظهار الأخطاء أثناء التطوير
    app.run(host='0.0.0.0', port=port, debug=True)
