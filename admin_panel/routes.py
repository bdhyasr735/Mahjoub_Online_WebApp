import os
import random
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import logout_user, login_required, current_user
from sqlalchemy import text
from core import db 
from . import admin_bp
from .auth import handle_admin_login

# --- 1. استيراد النماذج (نظام الوحدات المستقلة) ---
from core.models.user import User

try:
    from core.models.product import Product
except ImportError:
    Product = None

try:
    from core.models.business import Order
except ImportError:
    Order = None

# --- 2. التحقق من الصلاحية الإدارية السيادية ---
def is_admin():
    return current_user.is_authenticated and getattr(current_user, 'role', '').lower() == 'admin'

# --- 3. المسارات الإدارية (مركز القيادة) ---

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if is_admin():
        return redirect(url_for('admin.admin_dashboard'))
    return handle_admin_login()

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("تم تأمين النظام وتفكيك الجلسة الإدارية بنجاح", "info")
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if not is_admin():
        flash("تنبيه: محاولة وصول غير مصرح بها للمنطقة السيادية", "danger")
        return redirect(url_for('main.index'))
    
    # --- منطق الإحصائيات الرشيق (صمام أمان ضد خطأ 500) ---
    try:
        # جلب الأعداد باستخدام استعلامات SQL مباشرة لضمان أقصى درجات الخفة والرشاقة
        suppliers_count = db.session.execute(text("SELECT COUNT(*) FROM users WHERE role = 'vendor'")).scalar() or 0
        users_count = db.session.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0
        
        # التأكد من سلامة جدول الطلبات قبل الاستعلام (لتجنب الخطأ الظاهر في image_f5bc5a.png)
        try:
            orders_count = db.session.execute(text("SELECT COUNT(*) FROM orders")).scalar() or 0
        except:
            orders_count = 0

        stats = {
            'suppliers_count': suppliers_count,
            'orders_count': orders_count,
            'users_count': users_count,
            'pending_withdrawals': 0
        }
        return render_template('dashboard.html', **stats)
        
    except Exception as e:
        # صمام أمان: في حال حدوث أي خطأ في القاعدة، تفتح الصفحة بأصفار بدلاً من الانهيار
        print(f"⚠️ Dashboard SQL Error: {str(e)}")
        return render_template('dashboard.html', suppliers_count=0, orders_count=0, users_count=0, pending_withdrawals=0)

# --- 4. النوافذ الإدارية (ربط الملفات من الصورة image_f629d1.png) ---

@admin_bp.route('/manage-suppliers')
@login_required
def manage_suppliers():
    if not is_admin(): return redirect(url_for('main.index'))
    
    # جلب قائمة الموردين لعرضهم في واجهة الإدارة
    suppliers = User.query.filter_by(role='vendor').all()
    return render_template('manage_suppliers.html', suppliers=suppliers)

@admin_bp.route('/wallets')
@login_required
def manage_wallets():
    if not is_admin(): return redirect(url_for('main.index'))
    return render_template('wallets.html')

@admin_bp.route('/withdraw-requests')
@login_required
def withdraw_requests():
    if not is_admin(): return redirect(url_for('main.index'))
    return render_template('withdraw_requests.html')

# --- 5. مسارات الطوارئ والتعميد السيادي ---

@admin_bp.route('/approve-vendor/<int:user_id>')
@login_required
def approve_vendor(user_id):
    """بروتوكول تعميد المورد لتفعيل تمرير المنتجات لمتجر قمرة"""
    if not is_admin(): return "Unauthorized", 403
    
    vendor = User.query.get(user_id)
    if vendor:
        vendor.is_active_account = True
        db.session.commit()
        flash(f"تم تعميد المورد {vendor.username} بنجاح. المنتجات جاهزة للتمرير.", "success")
    return redirect(url_for('admin.manage_suppliers'))

@admin_bp.route('/make-me-admin')
@login_required
def make_me_admin():
    """مسار الطوارئ لترقية حساب علي محجوب إلى آدمن سيادي"""
    try:
        current_user.role = 'admin'
        db.session.commit()
        flash("تمت ترقيتك لآدمن سيادي بنجاح! الترسانة تحت تصرفك الآن.", "success")
        return redirect(url_for('admin.admin_dashboard'))
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}"
