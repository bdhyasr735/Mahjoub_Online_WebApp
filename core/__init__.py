# core/__init__.py
from flask import Flask
from flask_login import LoginManager
from .extensions import db  # استدعاء db من الهيكلية المعتمدة للنظام

# إعداد مدير تسجيل الدخول لضمان أمان مركز القيادة السيادي
login_manager = LoginManager()

def create_app():
    # 1. تهيئة التطبيق مع تحديد مسارات القوالب والملفات الثابتة العامة
    app = Flask(__name__, 
                static_folder='../static', 
                template_folder='../templates')
    
    # 2. تحميل الإعدادات من ملف Config السيادي (قاعدة البيانات، المفاتيح السرية)
    app.config.from_object('config.Config')
    
    # 3. ربط الإضافات (Extensions) بالتطبيق
    db.init_app(app)
    login_manager.init_app(app)
    
    # تحديد صفحة تسجيل الدخول الافتراضية للتحويل التلقائي
    login_manager.login_view = 'admin.login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى الترسانة السيادية"
    login_manager.login_message_category = "info"

    with app.app_context():
        # 4. استدعاء الموديلات (Models) لضمان تسجيل الجداول في النواة
        # استيراد Supplier هنا يضمن تفعيل نظام الأرصدة الثلاثية في القاعدة
        from .models.user import User
        from .models.supplier import Supplier
        
        # 5. تعميد الجداول (Database Synchronization)
        # سيقوم بإنشاء الجداول المفقودة تلقائياً دون المساس بالبيانات الموجودة
        db.create_all()
        
        # 6. تسجيل لوحة تحكم "محجوب أونلاين" (Blueprint Registration)
        try:
            from admin_panel import admin_bp
            # ربط بوابة الإدارة بالمسار المعتمد /admin لضمان عزل الصلاحيات
            app.register_blueprint(admin_bp) 
            # ملاحظة: الـ url_prefix مضاف مسبقاً في تعريف الـ Blueprint في ملفه الخاص
        except ImportError as e:
            # في حال عدم وجود المجلد أو خطأ في الاستيراد، يتم تسجيل التحذير
            print(f"⚠️ Warning: Admin Panel could not be registered. Error: {e}")

        # 7. بروتوكول استعادة المستخدم (User Loader)
        # المحرك الذي يتعرف على "علي محجوب" عند دخوله للمنظومة
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

    return app
