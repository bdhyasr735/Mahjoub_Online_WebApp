import os
import random
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import logout_user, login_required, current_user
from sqlalchemy import text
from core import db 
from . import admin_bp
from .auth import handle_admin_login

# --- 1. استيراد النماذج (تم تنظيف الاستدعاءات المحذوفة) ---
# تم حذف Vendor و WithdrawRequest لأنهما غير موجودين حالياً
from core.models.user import User

# محاولة استيراد النماذج الثانوية لتجنب الانهيار
try:
    from core.models.product import Product
except ImportError:
    Product = None

try:
    from core.models.business import Order
except ImportError:
    Order = None

# --- 2. خدمات الهوية المؤقتة ---
def generate_vendor_wallet():
    return f"W-MAH-{random.randint(100000, 999999)}"

def get_next_sovereign_id():
    # معرف وهمي لأن موديل Vendor محذوف
    return f"MAH-963-{random.randint(100, 999)}"

# --- 3. تأمين الوصول والمصادقة ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if getattr(current_user, 'role', '') == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
    return handle_admin_login()

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("تم تأمين النظام وتسجيل الخروج بنجاح", "info")
    return redirect(url_for('admin.login'))

# --- 4. لوحة التحكم (مركز المراقبة) ---
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if getattr(current_user, 'role', '') != 'admin':
        flash("عذراً، لا تمتلك صلاحيات الوصول للترسانة الإدارية", "danger")
        return redirect(url_for('main.index'))
    
    # إحصائيات ثابتة لتجنب الانهيار بسبب الموديلات المحذوفة
    stats = {
        'suppliers_count': 0, # لا يوجد موديل Vendor حالياً
        'pending_withdrawals': 0, # لا يوجد موديل WithdrawRequest حالياً
        'orders_count': db.session.query(Order).count() if Order else 0
    }
    return render_template('dashboard.html', **stats, show_repair=not session.get('repair_done'))

# --- 5. حوكمة الموردين (تم تعطيلها مؤقتاً لحين بناء الموديلات الجديدة) ---
@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if getattr(current_user, 'role', '') != 'admin':
        return "Unauthorized", 403
    
    # هذه الصفحة ستعرض رسالة تنبيه فقط لأن الموديل محذوف
    flash("نظام الموردين قيد التحديث الهيكلي حالياً", "warning")
    return render_template('add_supplier.html', 
                           next_id=get_next_sovereign_id(), 
                           next_wallet=generate_vendor_wallet())

# --- 6. مسار الترميم الهيكلي (الطوارئ) ---
@admin_bp.route('/force-repair-now')
@login_required
def force_repair():
    if getattr(current_user, 'role', '') != 'admin':
        return "Unauthorized", 403
    try:
        # تعطيل التعديلات على الجداول المحذوفة
        session['repair_done'] = True
        flash("تم تشغيل بروتوكول الإصلاح الصامت", "success")
        return redirect(url_for('admin.admin_dashboard'))
    except Exception as e:
        return f"Repair Error: {str(e)}"
