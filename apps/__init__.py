# apps/__init__.py
# coding: utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 1️⃣ أولاً: إنشاء الكائنات الأساسية وتصديرها فوراً للذاكرة لتكون متاحة لأي ملف يستوردها
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # تحميل إعدادات السيرفر وقاعدة البيانات الخاصة بك هنا
    # app.config.from_object(Config)

    # 2️⃣ ثانياً: ربط الكائنات مع التطبيق الحالي
    db.init_app(app)
    login_manager.init_app(app)

    # -------------------------------------------------------------------------
    # 🚨 التعديل الجوهري: تسجيل المسارات والبلوبرينتس في الأسفل تماماً بعد استقرار النواة
    # -------------------------------------------------------------------------
    
    # استدعاء وتسجيل موديل الموردين ليكون مرئياً لقاعدة البيانات
    from apps.models.supplier_db import Supplier

    # تسجيل البلوبرينت الجديد الخاص بإضافة الموردين لـ "منصة محجوب أونلاين"
    from apps.add_supplier.routes import admin_suppliers
    app.register_blueprint(admin_suppliers, url_prefix='/admin/suppliers')

    # 🛡️ تسجيل بقية الـ Blueprints الخاصة بالـ Dashboard والهيكل القديم هنا:
    # من الضروري ترك بقية تسجيلات الـ Blueprints القديمة الخاصة بنظامك هنا في الأسفل
    # مثال:
    # from apps.dashboard import dashboard_blueprint
    # app.register_blueprint(dashboard_blueprint)

    return app
