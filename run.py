from flask import Flask, redirect, url_for
import os
from models.admin_db import db, AdminUser
from models.supplier_db import Supplier

app = Flask(__name__)

# --- إعدادات السيادة والحماية ---
app.secret_key = os.environ.get('SECRET_KEY') or 'MAHJOUB_CENTRAL_SECURE_2026'

database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///mahjoub_admin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 1. ربط SQLAlchemy فوراً
db.init_app(app)

# 2. إنشاء الجداول "قبل" تسجيل الـ Blueprints (هذا هو السر)
with app.app_context():
    try:
        db.create_all()
        print("✅ تم تعميد الجداول بنجاح قبل تشغيل المسارات.")
    except Exception as e:
        print(f"⚠️ تنبيه: تعذر إنشاء الجداول: {e}")

# 3. تسجيل البوابات الرقمية بعد ضمان وجود القاعدة
try:
    from apps.admin_dashboard.routes import admin_bp
    from apps.auth_portal.routes import auth_bp
    from apps.add_supplier.routes import add_supplier_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(add_supplier_bp)
except Exception as e:
    print(f"❌ خطأ في ربط المسارات: {e}")

@app.route('/')
def root():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
