# coding: utf-8
# 📂 apps/auth_portal/routes.py

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from apps.models.admin_db import AdminUser

# [التنظيم السيادي]: تعريف الـ Blueprint
auth_portal = Blueprint(
    'auth_portal', 
    __name__, 
    template_folder='templates',
    url_prefix='/auth'
)

# [صمام الخصوصية]: مسار الدخول
LOGIN_PATH = os.environ.get('ADMIN_LOGIN_PATH', '/m7jb_sovereign_hq_v2_99x')

@auth_portal.route(LOGIN_PATH, methods=['GET', 'POST'])
def login():
    # منع إعادة الدخول للمسؤولين المتصلين بالفعل
    if current_user.is_authenticated:
