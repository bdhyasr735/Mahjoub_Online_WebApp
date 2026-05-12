from flask import Flask, redirect, url_for
import os

# 1. استدعاء المرجع الموحد لقاعدة البيانات والموديلات
# ملاحظة: استيراد Supplier هنا إلزامي لكي يتمكن db.create_all من رؤية الجدول وإنشائه
from models.admin_db import db, AdminUser
from models.supplier_db import Supplier

# 2. استيراد البوابات (Blueprints) مع معالجة احتمالية خطأ في المسارات
try:
    from apps.admin_dashboard.routes import admin_bp
    from apps.auth_portal.routes import auth_bp
    from apps.add_supplier.routes import add_supplier_bp
except ImportError as e:
    print(f"❌ خطأ تقني في استيراد المسارات (Blueprints): {e}")

app = Flask(__name__)

# --- 3. إعدادات الحماية والسيادة الرقمية ---

# مفتاح السر لتأمين الجلسات ومنع التلاعب
app.secret_key = os.environ.get('SECRET_KEY') or 'MAHJOUB_CENTRAL_SECURE_2026'

# إعداد وتوافق رابط قاعدة البيانات (تحويل postgres إلى postgresql لبيئة Railway)
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///mahjoub_admin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- 4. ربط وتعميد المكونات المركزية ---

# ربط كائن SQLAlchemy الموحد بالتطبيق
db.init_app(app)

# تسجيل البوابات (Blueprints) في مساراتها الرسمية
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(add_supplier_bp) # المسار الداخلي معرف بـ /supplier/add

@app.route('/')
def root():
    """ التوجيه التلقائي للمؤسس نحو بوابة الدخول """
    return redirect(url_for('auth.login'))

# --- 5. تأسيس قاعدة البيانات (Database Initialization) ---

def setup_database():
    """ وظيفة تضمن بناء الجداول في Postgres فور إقلاع السيرفر """
    with app.app_context():
        try:
            # إنشاء كافة الجداول المعرفة في الموديلات المستوردة
            db.create_all()
            print("✅ تم تعميد جميع الجداول (Admin & Supplier) في Postgres بنجاح.")
        except Exception as e:
            print(f"⚠️ تحذير: فشل تأسيس الجداول أو الجدول موجود مسبقاً: {e}")

# --- 6. تشغيل المحرك المركزي ---

if __name__ == '__main__':
    # تنفيذ فحص وتأسيس الجداول قبل بدء استقبال الطلبات
    setup_database()
    
    # تحديد المنفذ (Port) المتوافق مع إعدادات Railway الديناميكية
    port = int(os.environ.get('PORT', 5000))
    
    # التشغيل على النطاق العام لضمان ظهور الموقع أونلاين
    app.run(host='0.0.0.0', port=port)
