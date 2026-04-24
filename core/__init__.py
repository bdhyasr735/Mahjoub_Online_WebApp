from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

# تعريف كائن قاعدة البيانات
db = SQLAlchemy()

def create_app():
    # 1. إنشاء نسخة التطبيق (بدون فرض مسار قوالب واحد ليدعم الـ Blueprints)
    app = Flask(__name__, static_folder='../static')
    
    # 2. تحميل الإعدادات من ملف config.py
    app.config.from_object(Config)
    
    # 3. تهيئة قاعدة البيانات مع التطبيق
    db.init_app(app)
    
    # 4. تسجيل الـ Blueprints (الأجزاء المختلفة للمشروع)
    try:
        from admin_panel.routes import admin_bp
        from supplier_panel.routes import supplier_bp
        from webhooks.routes import webhooks_bp
        
        # ربط لوحة الإدارة بمسار /admin
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(supplier_bp, url_prefix='/supplier')
        app.register_blueprint(webhooks_bp, url_prefix='/webhooks')
        
        print("✅ تم تسجيل جميع الـ Blueprints بنجاح.")
    except ImportError as e:
        print(f"❌ خطأ في استيراد الـ Blueprints: {e}")

    # 5. صفحة رئيسية بسيطة للفحص السريع (Health Check)
    @app.route('/')
    def index():
        return """
        <div style="text-align:center; margin-top:50px; font-family:Arial; direction:rtl;">
            <h1 style="color: #4B0082;">نظام محجوب أونلاين يعمل بنجاح!</h1>
            <p>السيرفر متصل حالياً، يمكنك الانتقال للوحة التحكم:</p>
            <a href="/admin/" style="display:inline-block; padding:10px 20px; background:#6a0dad; color:white; text-decoration:none; border-radius:5px;">دخول لوحة الإدارة</a>
        </div>
        """

    # 6. طباعة خريطة المسارات في الـ Logs للتأكد عند التشغيل
    with app.app_context():
        print("🔗 قائمة المسارات النشطة في النظام:")
        for rule in app.url_map.iter_rules():
            print(f"-> {rule}")

    return app
