import os
from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# 1. تعريف الكائنات الأساسية
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # 2. جلب الإعدادات من بيئة Render (Environment Variables)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mahjoub_online_default_key_9046')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 3. تهيئة الإضافات
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'supplier_panel.login'

    # 4. نظام التوجيه الذكي (بدون أسماء ثابتة معقدة)
    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith('/admin_control_9046'):
            return redirect(url_for('admin_panel.admin_login'))
        return redirect(url_for('supplier_panel.login'))

    with app.app_context():
        # استيراد النماذج (Models)
        from core import models
        
        # 5. تسجيل البوابات (Blueprints) بطريقة مرنة
        # تسجيل الموردين
        try:
            from supplier_panel import supplier_bp
            app.register_blueprint(supplier_bp, url_prefix='/supplier')
        except Exception as e:
            print(f"⚠️ لم يتم تحميل بوابة الموردين: {e}")

        # تسجيل الإدارة (البحث التلقائي عن أي كائن Blueprint داخل المجلد)
        try:
            import admin_panel
            for item in dir(admin_panel):
                obj = getattr(admin_panel, item)
                # إذا وجدنا أي كائن من نوع Blueprint، نقوم بتسجيله فوراً
                if str(type(obj)) == "<class 'flask.blueprints.Blueprint'>":
                    app.register_blueprint(obj, url_prefix='/admin_control_9046')
                    print(f"✅ تم تفعيل بوابة الإدارة بنجاح")
        except Exception as e:
            print(f"⚠️ فشل استيراد مجلد الإدارة: {e}")

        db.create_all()

    return app

app = create_app()

@login_manager.user_loader
def load_user(user_id):
    from core.models import User
    return User.query.get(int(user_id))
