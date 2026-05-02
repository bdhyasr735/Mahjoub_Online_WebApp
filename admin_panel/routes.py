import os
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import text
from core import db 

# استيراد النماذج بحذر شديد
try:
    from core.models.user import User
    from core.models.vendor import Vendor
except ImportError:
    User = None
    Vendor = None

try:
    from core.models.vendor import WithdrawRequest 
except ImportError:
    WithdrawRequest = None

from . import admin_bp
from .auth import handle_admin_login

# --- 1. نظام الإصلاح التلقائي ---
@admin_bp.route('/system-repair-sovereign')
@login_required
def auto_repair():
    db.session.rollback()
    try:
        # تنفيذ الأمر مباشرة على محرك القاعدة لتجنب مشاكل الـ ORM
        db.engine.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS user_id INTEGER;"))
        db.session.commit()
        session['repair_done'] = True # حفظ حالة الإصلاح في الجلسة
        flash("تم تفعيل الترميم السيادي بنجاح.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"فشل الإصلاح: {str(e)}", "danger")
    return redirect(url_for('admin.admin_dashboard'))

# --- 2. بوابة الولوج السيادي ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    db.session.rollback()
    if current_user.is_authenticated:
        # استخدام getattr لتجنب الأخطاء إذا كان الكائن ناقصاً
        role = getattr(current_user, 'role', None)
        if role == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
    return handle_admin_login()

# --- 3. لوحة التحكم المركزية (الداشبورد) ---
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    # 🛡️ تنظيف فوري للجلسة
    db.session.rollback()
    
    # تحضير الإحصائيات (قيم صفرية افتراضية)
    stats = {
        'suppliers_count': 0,
        'pending_withdrawals': 0,
        'orders_count': 0,
        'total_balance': "0.00"
    }

    show_repair = not session.get('repair_done', False)

    try:
        # محاولة جلب الأرقام فقط إذا كان الموديل متاحاً والقاعدة مستقرة
        if Vendor:
            stats['suppliers_count'] = db.session.query(Vendor).count()
        if WithdrawRequest:
            stats['pending_withdrawals'] = db.session.query(WithdrawRequest).filter_by(status='pending').count()
    except Exception as e:
        # إذا حدث خطأ هنا، فهذا يؤكد وجود مشكلة في هيكل الجدول
        db.session.rollback()
        show_repair = True 
        print(f"⚠️ Dashboard SQL Error: {str(e)}")

    # إرجاع القالب مهما حدث
    return render_template('dashboard.html', 
                           suppliers_count=stats['suppliers_count'],
                           pending_withdrawals=stats['pending_withdrawals'],
                           orders_count=stats['orders_count'],
                           total_balance=stats['total_balance'],
                           show_repair=show_repair)

# --- 4. تسجيل الخروج ---
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('تم إغلاق الجلسة الآمنة.', 'info')
    return redirect(url_for('admin.login'))
