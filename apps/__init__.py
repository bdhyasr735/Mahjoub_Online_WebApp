# coding: utf-8
import os
import importlib
from flask import Flask
from apps.extensions import db, login_manager, migrate
from apps.models.admin_db import AdminUser
from apps.models import Supplier

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # تهيئة الإضافات
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    with app.app_context():
        # 1. بناء الجداول تلقائياً
        try:
            db.create_all()
            print("✅ [Database]: تم فحص وبناء الجداول بنجاح.")
        except Exception as e:
            print(f"⚠️ [Database]: خطأ أثناء محاولة بناء الجداول: {e}")

        # 2. إنشاء المستخدمين تلقائياً (إدارة + مورد)
        try:
            # إضافة مدير النظام: علي محجوب
            if not AdminUser.query.filter_by(username='علي محجوب').first():
                admin = AdminUser(username='علي محجوب', role='Owner')
                admin.set_password('123')
                db.session.add(admin)
                print("✅ [Admin]: تم إنشاء
