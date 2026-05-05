import os
from flask import render_template, request, redirect, url_for, flash
from flask_login import logout_user, login_required, current_user
from sqlalchemy import text
from core import db 
from . import admin_bp
from .auth import handle_admin_login

# --- 1. التحقق من الصلاحية (علي محجوب فقط) ---
def is_admin_sovereign():
    return current_user.is_authenticated and getattr(current_user, 'role', '').lower() == 'admin'

# --- 2. مركز القيادة (الداشبورد المصفح) ---
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if not is_admin_sovereign():
        return redirect(url_for('main.index'))
    
    try:
        # استعلامات مباشرة (Direct SQL) لتجنب انهيار الموديلات
        # نجلب الأعداد من الجداول التي قمت بترميمها في الصور f61295 و f5bc5a
        suppliers = db.session.execute(text("SELECT COUNT(*) FROM users WHERE role = 'vendor'")).scalar() or 0
        total_users = db.session.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0
        
        # تجنب الانهيار في حال لم يُنشأ جدول الطلبات بعد
        try:
            total_orders = db.session.execute(text("SELECT COUNT(*) FROM orders")).scalar() or 0
        except:
            total_orders = 0

        stats = {
            'suppliers_count': suppliers,
            'orders_count': total_orders,
            'users_count': total_users,
            'pending_withdrawals': 0
        }
        return render_template('dashboard.html', **stats)
        
    except Exception as e:
        print(f"⚠️ Dashboard Crash Avoided: {str(e)}")
        # إذا حدث أي خطأ، نعرض أصفاراً بدلاً من صفحة 500
        return render_template('dashboard.html', suppliers_count=0, orders_count=0, users_count=0, pending_withdrawals=0)

# --- 3. بقية المسارات الرشيقة ---
@admin_bp.route('/manage-suppliers')
@login_required
def manage_suppliers():
    if not is_admin_sovereign(): return redirect(url_for('main.index'))
    
    # جلب الموردين من قاعدة البيانات مباشرة
    result = db.session.execute(text("SELECT id, username, email, is_active_account FROM users WHERE role = 'vendor'"))
    suppliers = result.fetchall()
    return render_template('manage_suppliers.html', suppliers=suppliers)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if is_admin_sovereign(): return redirect(url_for('admin.admin_dashboard'))
    return handle_admin_login()

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))
