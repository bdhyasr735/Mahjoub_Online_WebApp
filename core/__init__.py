from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

# 1. تعريف كائن قاعدة البيانات المركزي
# هذا الكائن هو الذي يجب استيراده في core/models.py عبر: from core import db
db = SQLAlchemy()

def create_app():
    # 2. إنشاء نسخة التطبيق وتحديد مجلد الملفات الثابتة (الصور والـ CSS)
    app = Flask(__name__, static_folder='../static')
    
    # 3. تحميل الإعدادات (DATABASE_URL, SECRET_KEY, etc.) من ملف config.py
    app.config.from_object(Config)
    
    # 4. تهيئة قاعدة البيانات مع نسخة التطبيق الحالية
    db.init_app(app)
    
    # 5. تسجيل الـ Blueprints لربط لوحات التحكم بالمسارات
    try:
        from admin_panel.routes import admin_bp
        from supplier_panel.routes import supplier_bp
        
        # ربط لوحة الإدارة (المسؤول) ولوحة الموردين
        # الآن سيعمل رابط /admin/sync_now بشكل تلقائي
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(supplier_bp, url_prefix='/supplier')
        
        print("✅ تم تسجيل Blueprints الإدارة والموردين بنجاح.")
    except ImportError as e:
        print(f"❌ خطأ في استيراد الـ Blueprints (تأكد من وجود ملفات routes): {e}")

    # 6. الواجهة الرئيسية الترحيبية لنظام "محجوب أونلاين"
    @app.route('/')
    def index():
        return """
        <div style="text-align:center; margin-top:50px; font-family: 'Segoe UI', Tahoma, sans-serif; direction:rtl;">
            <h1 style="color: #6a0dad;">🚀 نظام محجوب أونلاين يعمل بنجاح!</h1>
            <p style="font-size: 18px; color: #555;">المحرك متصل الآن بقاعدة بيانات رندر وبوابة قمرة.</p>
            <div style="margin-top: 30px;">
                <a href="/admin/sync_now" style="display:inline-block; padding:15px 30px; background:#6a0dad; color:white; text-decoration:none; border-radius:25px; font-weight:bold; box-shadow: 0 4px 10px rgba(106, 13, 173, 0.3); transition: 0.3s;">
                    دخول عرض المنتجات اللحظي ⬅️
                </a>
            </div>
        </div>
        """

    # 7. فحص المسارات النشطة عند الإقلاع (يظهر في سجلات Railway السوداء)
    with app.app_context():
        print("🔗 المسارات المتاحة حالياً في النظام:")
        for rule in app.url_map.iter_rules():
            print(f"-> {rule}")

    return app
