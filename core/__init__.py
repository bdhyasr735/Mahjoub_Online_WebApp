from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# تهيئة الكائنات الأساسية خارج الدالة لمنع التكرار
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    """
    دالة بناء التطبيق (Application Factory)
    تجمع النواة، الموديلات، وبوابات الإدارة في كيان واحد.
    """
    app = Flask(__name__)

    # إعدادات المحرك (تأكد من ضبط قاعدة البيانات لتدعم UTF-8 للأسماء العربية)
    app.config['SECRET_KEY'] = 'Mahjoub_Sovereign_2026_Key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/mahjoub_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # تفعيل الإضافات داخل سياق التطبيق
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # توجيه المستخدمين غير المسجلين إلى بوابة الولوج السيادي
    login_manager.login_view = 'admin_panel.admin_login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى برج الرقابة."
    login_manager.login_message_category = "info"

    with app.app_context():
        # تسجيل بوابة الإدارة (Blueprint)
        from admin_panel.routes import admin_panel
        app.register_blueprint(admin_panel, url_prefix='/admin')

        # استدعاء الموديلات لضمان بناء الجداول (User, Supplier, Product)
        from core import models

    return app

@login_manager.user_loader
def load_user(user_id):
    """
    محرك التحقق من الهوية: يقوم باستعادة المستخدم من قاعدة البيانات عبر معرفه.
    """
    from core.models.user import User
    return User.query.get(int(user_id))
