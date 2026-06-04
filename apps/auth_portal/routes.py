# coding: utf-8
# 📂 apps/auth_portal/routes.py - مسارات الدخول المباشر المحصنة والمشفرة

import os
import time
import random
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from apps.extensions import db
from . import auth_portal
from apps.models.admin_db import AdminUser

# مسار الدخول السري (يُجلب من إعدادات البيئة)
SECRET_LOGIN_PATH = os.environ.get('ADMIN_LOGIN_PATH', '/m7jb_sovereign_hq_v2_99x')

# -------------------------------------------------------------------------
# 1. المسار السري (الدخول المباشر)
# -------------------------------------------------------------------------
@auth_portal.route(SECRET_LOGIN_PATH, methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard.dashboard'))

    if request.method == 'POST':
        # استخدام .strip() لمنع أخطاء المسافات الزائدة
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # 🛡️ تأخير زمني عشوائي لإحباط هجمات القوة الغاشمة (Brute Force)
        time.sleep(random.uniform(1.0, 2.0))
        
        try:
            user = AdminUser.query.filter_by(username=username).first()
            
            # 1. التحقق من وجود اسم المستخدم
            if not user:
                flash('اسم المستخدم غير مسجل في المنصة اللامركزية.', 'danger')
                return render_template('auth/login.html')

            # 2. التحقق من القفل (تجاوز المحاولات الخاطئة)
            if hasattr(user, 'is_locked') and user.is_locked():
                flash('الحساب مقفل مؤقتاً بسبب كثرة المحاولات.', 'danger')
                return render_template('auth/login.html')
            
            # 3. التحقق من كلمة المرور
            if user.check_password(password):
                if user.role in ['Owner', 'Admin']:
                    login_user(user)
                    if hasattr(user, 'reset_failed_attempts'):
                        user.reset_failed_attempts()
                        db.session.commit()
                    return redirect(url_for('admin_dashboard.dashboard'))
                else:
                    flash('ليس لديك صلاحية الدخول لهذه البوابة.', 'danger')
            else:
                # كلمة المرور غير صحيحة
                if hasattr(user, 'increment_failed_attempts'):
                    user.increment_failed_attempts()
                    db.session.commit()
                flash('كلمة المرور غير صحيحة.', 'danger')
                    
        except Exception as e:
            # تسجيل الخطأ في السجلات (Logs) وليس للمستخدم مباشرة
            print(f"🚨 خطأ فني في بوابة الدخول: {e}")
            flash('حدث خطأ في الاتصال بالمنصة، يرجى المحاولة لاحقاً.', 'warning')
    
    return render_template('auth/login.html')

# -------------------------------------------------------------------------
# 2. مسار الكمين (Decoy) - لمنع الزحف التلقائي (Bots Crawling)
# -------------------------------------------------------------------------
@auth_portal.route('/login', methods=['GET', 'POST'])
def decoy_login():
    # أي محاولة وصول لهذا المسار ستؤدي لحظر الطلب
    abort(403)

# -------------------------------------------------------------------------
# 3. تسجيل الخروج
# -------------------------------------------------------------------------
@auth_portal.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_portal.login'))

# -------------------------------------------------------------------------
# 4. مسار الهوية (مغلق ومحمي)
# -------------------------------------------------------------------------
@auth_portal.route('/upload-identity', methods=['GET', 'POST'])
@login_required
def upload_identity():
    return render_template('auth/upload_id.html')
