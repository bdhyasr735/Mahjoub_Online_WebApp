# coding: utf-8
# 📂 apps/__init__.py

import os
import importlib
from flask import Flask, redirect, session, url_for, request
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS 
from werkzeug.routing import BuildError
from jinja2 import ChoiceLoader, FileSystemLoader  # 👈 أضف هذا الاستيراد
import config
from apps.extensions import db, login_manager, migrate

# تهيئة الأدوات
csrf = CSRFProtect()
talisman = Talisman()
limiter = Limiter(key_func=get_remote_address, default_limits=["500 per day", "100 per hour"], storage_uri="memory://")

ADMIN_MODULES = {}
SUPPLIER_MODULES = {}

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    config.Config.validate_config()

    # 🟣 حل ديناميكي وتلقائي لمشكلة TemplateNotFound لجميع القوالب الأساسية
    # بحيث يرى الجميع مجلد قوالب admin_dashboard تلقائياً دون تكرار
    base_template_path = os.path.join(app.root_path, 'admin_dashboard', 'templates')
    if os.path.exists(base_template_path):
        app.jinja_loader = ChoiceLoader([
            app.jinja_loader,
            FileSystemLoader(base_template_path)
        ])

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=os.environ.get('FLASK_ENV') == 'production',
        SESSION_COOKIE_SAMESITE='Lax',
    )
    # ... (باقي كود التهيئة كما هو بدون تغيير)
