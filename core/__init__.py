from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

# تعريف كائن قاعدة البيانات المركزي (خارج الدالة لمنع التكرار)
db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_folder='../static')
    
    # تحميل الإعدادات
    app.config.from_object(Config)
    
    # تهيئة قاعدة البيانات
    db.init_app(app)
    
    with app.app_context():
        # كسر الحلقة الدائرية: استيراد المودلز والـ Blueprints هنا فقط
        try:
            # استيراد النماذج للتأكد من ربطها بـ db
            from core import models
            
            # استيراد الـ Blueprints
            from admin_panel.routes import admin_bp
            from supplier_panel.routes import supplier_bp
            
            # تسجيل المسارات
            app.register_blueprint(admin_bp, url_prefix='/admin')
            app.register_blueprint(supplier_bp, url_prefix='/supplier')
            
            print("✅ تم كسر الحلقة الدائرية وتسجيل جميع المسارات بنجاح.")
        except Exception as e:
            print(f"❌ خطأ تقني في الربط: {e}")

    # الواجهة الترحيبية الأساسية
    @app.route('/')
    def index():
        return """
        <div style="text-align:center; margin-top:50px; font-family: sans-serif; direction:rtl;">
            <h1 style="color: #6a0dad;">🚀 منصة محجوب أونلاين</h1>
            <p>النظام متصل الآن وبانتظار دخولك للوحة التحكم.</p>
            <a href="/admin/" style="display:inline-block; padding:10px 20px; background:#6a0dad; color:white; text-decoration:none; border-radius:5px;">دخول لوحة الإدارة ⬅️</a>
        </div>
        """

    # فحص المسارات المتاحة (للتأكد في سجلات Railway)
    with app.app_context():
        print("🔗 قائمة المسارات النشطة:")
        for rule in app.url_map.iter_rules():
            print(f"-> {rule}")

    return app
