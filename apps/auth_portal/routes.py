# coding: utf-8
# 🔑 بوابة النفاذ السيادية - منصة محجوب أونلاين 2026
# هذا الملف يدير عمليات التحقق الرقمي والولوج الآمن إلى لوحة التحكم الإدارية

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from apps.extensions import db
from apps.models.admin_db import AdminUser

# استيراد البلوبرينت من نفس الحزمة الفرعية
from . import auth_blueprint

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # منع الدخول المتكرر إذا كانت الجلسة الرقمية نشطة بالفعل لضمان انسيابية الحركة
    if current_user.is_authenticated:
        try:
            return redirect(url_for('admin_dashboard.dashboard'))
        except Exception:
            # توجيه سيادي احتياطي في حال اختلاف المسمى البرمجي للمسار الرئيسي
            return redirect('/')

    if request.method == 'POST':
        # تنظيف المدخلات الرقمية لمنع الثغرات وإزالة الفراغات العشوائية
        username = str(request.form.get('username', '')).strip()
        password = request.form.get('password', '')
        
        # استعلام مباشر عبر المعرّف الفرعي المفهرس في قاعدة البيانات
        user = AdminUser.query.filter_by(username=username).first()
        
        # 🛡️ استدعاء بوابة التحقق المغلفة والمحمية داخل الموديل مباشرة (Encapsulation)
        if user and user.check_password(password):
            
            # التحقق من امتلاك صلاحيات القيادة الإدارية العليا للمنصة
            if user.role in ['Owner', 'Admin']:
                login_user(user)
                
                # تحديث طابع الوقت السيادي عبر خادم قاعدة البيانات مباشرة لتوثيق النفاذ
                user.last_login = db.func.current_timestamp()
                db.session.commit()
                
                flash('مرحباً بك في سوقك الذكي. تم توثيق النفاذ بنجاح.', 'success')
                try:
                    return redirect(url_for('admin_dashboard.dashboard'))
                except Exception:
                    return redirect('/')
            else:
                flash('ليس لديك صلاحيات الوصول لهذه المنطقة السيادية.', 'warning')
        else:
            flash('بيانات الدخول غير صحيحة، يرجى التحقق من الهوية الرقمية.', 'danger')
    
    return render_template('auth/login.html')

@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج من المنطقة السيادية بنجاح.', 'info')
    
    # ⚡ تم الإصلاح: التوجيه بالاعتماد على الاسم النصي المسجل للبلوبرينت (auth_portal) لمنع انهيار السيرفر بـ BuildError
    return redirect(url_for('auth_portal.login'))
