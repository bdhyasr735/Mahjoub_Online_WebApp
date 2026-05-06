# core/__init__.py
from flask import Flask
from flask_login import LoginManager
from .extensions import db  # استدعاء db من الهيكلية المعتمدة للنظام

# إعداد مدير تسجيل الدخول لضمان أمان مركز القيادة
login_manager = LoginManager()

def create_app():
    # تهيئة التطبيق مع تحديد مسارات القوالب والملفات الثابتة
    app = Flask(__name__, 
                static_folder='../static', 
                template_folder='../templates')
    
    # تحميل الإعدادات من ملف Config السيادي
    app.config.from_object('config.Config')
    
    # ربط الإضافات (Extensions) بالتطبيق لضمان عمل قاعدة البيانات
    db.init_app(app)
    login_manager.init_app(app)
    
    # تحديد صفحة تسجيل الدخول الافتراضية
    login_manager.login_view = 'admin.login'

    with app.app_context():
        # استدعاء الموديلات (Models) لضمان تسجيل الجداول في النواة
        # استيراد Supplier يضمن تفعيل حقل "الرتبة" في قاعدة البيانات
        from .models.user import User
        from .models.supplier import Supplier
        
        # تعميد الجداول وإنشاؤها تلقائياً عند التشغيل الأول
        db.create_all()
        
        # تسجيل لوحة تحكم "محجوب أونلاين" (Blueprint)
        try:
            from admin_panel import admin_bp
            # ربط بوابة الإدارة بالمسار المعتمد /admin
            app.register_blueprint(admin_bp, url_prefix='/admin')
        except ImportError:
            # في حال عدم وجود المجلد، يستمر النظام في العمل دون توقف التردد
            pass

        # بروتوكول استعادة المستخدم للتحقق من الصلاحيات السيادية
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

    return app
