from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

# تعريف الكائن المركزي لقاعدة البيانات
db = SQLAlchemy()

def create_app():
    # إعداد التطبيق وتحديد مجلد الملفات الثابتة
    app = Flask(__name__, static_folder='../static')
    app.config.from_object(Config)
    
    # تهيئة قاعدة البيانات
    db.init_app(app)
    
    with app.app_context():
        # كسر الحلقة الدائرية عبر الاستيراد المتأخر داخل الـ context
        try:
            # 1. استيراد المودلز
            from core import models
            
            # 2. استيراد وتسجيل البلوبرنت للإدارة (وهو الأهم الآن)
            from admin_panel.routes import admin_bp
            app.register_blueprint(admin_bp, url_prefix='/admin')
            
            # 3. استيراد وتسجيل بلوبرنت الموردين
            from supplier_panel.routes import supplier_bp
            app.register_blueprint(supplier_bp, url_prefix='/supplier')
            
            print("✅ تم تسجيل جميع البوابات (admin & supplier) بنجاح.")
        except Exception as e:
            # في حال وجود خطأ في ملف واحد، لا ينهار السيرفر بالكامل
            print(f"⚠️ تنبيه: حدث خطأ أثناء تحميل بعض المسارات: {e}")

    # الصفحة الرئيسية الترحيبية
    @app.route('/')
    def index():
        return """
        <div style="text-align:center; margin-top:50px; font-family: sans-serif; direction:rtl;">
            <h1 style="color: #6a0dad;">🚀 منصة محجوب أونلاين</h1>
            <p>المحرك يعمل الآن. للدخول إلى الإدارة، اضغط على الزر أدناه:</p>
            <div style="margin-top: 20px;">
                <a href="/admin/" style="display:inline-block; padding:15px 30px; background:#6a0dad; color:white; text-decoration:none; border-radius:25px; font-weight:bold;">
                    دخول لوحة الإدارة ⬅️
                </a>
            </div>
        </div>
        """

    # طباعة المسارات في السجلات للتشخيص
    with app.app_context():
        print("🔗 قائمة المسارات المتاحة حالياً في Railway:")
        for rule in app.url_map.iter_rules():
            print(f"-> {rule}")

    return app
