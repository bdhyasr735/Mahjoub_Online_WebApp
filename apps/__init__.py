# coding: utf-8
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# الكائنات المركزية
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)
    
    app.json.ensure_ascii = False
    db.init_app(app)
    login_manager.init_app(app)

    # ... (بقية كود تهيئة قاعدة البيانات الخاص بك كما هو) ...

    # 📥 الاستيراد الصحيح (تم تعديل السطر ليطابق الاسم في ملف الداشبورد)
    from apps.admin_dashboard.routes import admin_dashboard
    from apps.auth_portal import auth_blueprint
    from apps.add_supplier.routes import admin_suppliers_bp
    from apps.wallet.routes import admin_wallet

    # ⚙️ تسجيل البلوبرينتس
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(admin_dashboard, url_prefix='/admin')
    app.register_blueprint(admin_suppliers_bp, url_prefix='/admin')
    app.register_blueprint(admin_wallet, url_prefix='/admin')

    return app
