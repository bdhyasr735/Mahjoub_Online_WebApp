from flask import Flask, redirect, url_for
import os

# 1. استدعاء المرجع الموحد لقاعدة البيانات والموديلات
# استيراد Supplier هنا ضروري جداً لضمان ظهوره في Railway
from models.admin_db import db, AdminUser
from models.supplier_db import Supplier

# 2. استيراد البوابات (Blueprints) مع معالجة الأخطاء
try:
    from apps.admin_dashboard.routes import admin_bp
    from apps.auth_portal.routes import auth_bp
    from apps.add_supplier.routes import add_supplier_bp
except ImportError as e:
    print(f"❌ خطأ في استيراد المسارات: {e}")

app = Flask(__name__)

# --- 3. إعدادات الحماية والسيادة الرقمية ---
# مفتاح السر لتأمين الجلسات (Sessions)
app.secret_key = os.environ.get('SECRET_KEY') or 'MAHJOUB_CENTRAL_SECURE_2026'

# ضبط مسار قاعدة البيانات (التوافق مع Railway Postgres)
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///mahjoub_admin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- 4. ربط المكونات وتعميد النظام ---
db.init_app(app)

# تسجيل البوابات الرقمية في مساراتها الصحيحة
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(add_supplier_bp) # المسار: /supplier/add

@app.route('/')
def root():
    """توجيه الزائر مباشرة إلى بوابة الدخول"""
    return redirect(url_for('auth.login'))

# --- 5. تأسيس المنظومة (Database Initialization) ---
def setup_database():
    """وظيفة تضمن إنشاء الجداول فور تشغيل السيرفر"""
    with app.app_context():
        try:
            db.create_all()
            print("✅ تم تعميد جميع الجداول (Admin & Supplier) في Postgres بنجاح.")
        except Exception as e:
            print(f"⚠️ فشل تأسيس الجداول: {e}")

# --- 6. نقطة الانطلاق ---
if __name__ == '__main__':
    setup_database()
    # تحديد المنفذ المتوافق مع بيئة Railway
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
