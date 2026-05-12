from flask import Flask, redirect, url_for
import os
# استدعاء محركات قواعد البيانات والموديلات
from models.admin_db import db, AdminUser
from models.supplier_db import Supplier

# استيراد البوابات (Blueprints) مع التأكد من المسميات الصحيحة للمجلدات
try:
    from apps.admin_dashboard.routes import admin_bp
    from apps.auth_portal.routes import auth_bp # تأكد أن المجلد اسمه auth_portal
    from apps.add_supplier.routes import add_supplier_bp # تأكد أن المجلد اسمه add_supplier
except ImportError as e:
    print(f"❌ خطأ في أسماء المجلدات: {e}")

app = Flask(__name__)

# --- إعدادات الحماية والسيادة ---
app.secret_key = os.environ.get('SECRET_KEY') or 'MAHJOUB_CENTRAL_SECURE_2026'

database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///mahjoub_admin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- ربط المكونات ---
db.init_app(app)

# تسجيل البوابات
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(add_supplier_bp) # المسار معرف داخلياً بـ /supplier/add

@app.route('/')
def root():
    return redirect(url_for('auth.login'))

# --- تأسيس الجداول ---
def setup_database():
    with app.app_context():
        db.create_all() # هذا سيجعل الجداول تظهر في Railway فوراً
        print("✅ تم تعميد الجداول في قاعدة البيانات بنجاح.")

if __name__ == '__main__':
    setup_database()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
