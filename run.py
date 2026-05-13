from flask import Flask, redirect, url_for
import os
from models.admin_db import db, AdminUser
from models.supplier_db import Supplier

app = Flask(__name__)

# --- إعدادات السيادة والحماية ---
# استخدام مفتاح سري قوي وتأمين قاعدة البيانات
app.secret_key = os.environ.get('SECRET_KEY') or 'MAHJOUB_CENTRAL_SECURE_2026'

database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    # إصلاح رابط قاعدة البيانات ليتوافق مع SQLAlchemy الحديثة
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///mahjoub_admin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 1. ربط SQLAlchemy بالمنظومة
db.init_app(app)

# 2. إنشاء الجداول وتعميد البيانات
with app.app_context():
    try:
        db.create_all()
        print("✅ تم تعميد الجداول بنجاح في منظومة محجوب.")
    except Exception as e:
        print(f"⚠️ تنبيه: تعذر إنشاء الجداول: {e}")

# 3. تسجيل البوابات الرقمية (Blueprints)
try:
    from apps.admin_dashboard.routes import admin_bp
    from apps.auth_portal.routes import auth_bp
    from apps.add_supplier.routes import add_supplier_bp
    
    # تسجيل بوابات المصادقة ولوحة التحكم
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # تسجيل بوابة الموردين تحت بادئة admin لضمان عمل url_for('admin.add_supplier')
    # ملاحظة: تأكد أن اسم الـ Blueprint داخل routes.py هو 'admin'
    app.register_blueprint(add_supplier_bp, url_prefix='/admin')
    
except Exception as e:
    print(f"❌ خطأ في ربط المسارات الرقمية: {e}")

@app.route('/')
def root():
    # توجيه الزوار تلقائياً إلى بوابة تسجيل الدخول
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    # تشغيل الخادم على المنفذ المخصص من البيئة السحابية
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
