import os
import random
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import logout_user, login_required, current_user
from sqlalchemy import text
from sqlalchemy.orm import joinedload
from core import db 
from werkzeug.security import generate_password_hash
from . import admin_bp
from .auth import handle_admin_login

# --- 1. استيراد النماذج (الهوية السيادية الموحدة) ---
from core.models.user import User
from core.models.vendor import Vendor, WithdrawRequest

# محاولة استيراد النماذج الثانوية لتجنب الانهيار في Railway
try:
    from core.models.business import Order
except ImportError:
    Order = None

# --- 2. خدمات الهوية والمحافظ السيادية ---
def generate_vendor_wallet():
    """توليد محفظة تبدأ بـ W-MAH لضمان الهوية المالية"""
    return f"W-MAH-{random.randint(100000, 999999)}"

def get_next_sovereign_id():
    """توليد المعرف السيادي MAH-963 بناءً على عدد الموردين الحاليين"""
    try:
        db.session.rollback()
        # حساب العدد الإجمالي للموردين المسجلين في القاعدة
        count = db.session.query(Vendor).count()
        return f"MAH-963{count + 1}"
    except Exception:
        # حل احتياطي في حال فشل الاتصال المؤقت بالقاعدة
        return f"MAH-963{random.randint(100, 999)}"

# --- 3. مسار الترميم الهيكلي (الطوارئ) ---
@admin_bp.route('/force-repair-now')
@login_required
def force_repair():
    if getattr(current_user, 'role', '') != 'admin':
        return "Unauthorized", 403
    try:
        db.session.rollback() 
        # تحديث الجداول برمجياً لضمان وجود الحقول السيادية
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS supplier_id VARCHAR(50) UNIQUE;"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS e_wallet VARCHAR(100) UNIQUE;"))
        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'vendor';"))
        
        db.session.commit()
        session['repair_done'] = True
        flash("تم ترميم هيكل الترسانة وتحديث المعرفات بنجاح", "success")
        return redirect(url_for('admin.admin_dashboard'))
    except Exception as e:
        db.session.rollback()
        return f"Repair Error: {str(e)}"

# --- 4. لوحة التحكم (مركز المراقبة) ---
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if getattr(current_user, 'role', '') != 'admin':
        return redirect(url_for('main.index'))
    
    stats = {
        'suppliers_count': db.session.query(Vendor).count(),
        'pending_withdrawals': db.session.query(WithdrawRequest).filter_by(status='pending').count(),
        'orders_count': db.session.query(Order).count() if Order else 0
    }
    return render_template('dashboard.html', **stats, show_repair=not session.get('repair_done'))

# --- 5. حوكمة الموردين (إضافة وتعميد مورد جديد) ---
@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        try:
            db.session.rollback()
            username = request.form.get('username')
            password = request.form.get('password')
            
            # التحقق من عدم تكرار المستخدم
            if User.query.filter_by(username=username).first():
                return jsonify({"status": "error", "message": "اسم المستخدم مسجل مسبقاً"}), 400

            # 1. إنشاء حساب الدخول (User)
            new_user = User(
                username=username,
                role='vendor'
            )
            new_user.set_password(password) # استخدام الدالة الآمنة من الموديل
            db.session.add(new_user)
            db.session.flush() 

            # 2. إنشاء بروفايل المورد السيادي (Vendor)
            new_vendor = Vendor(
                user_id=new_user.id,
                supplier_id=request.form.get('next_id'), # حفظ المعرف السيادي
                trade_name=request.form.get('trade_name'),
                owner_name=request.form.get('owner_name'),
                phone=request.form.get('phone'),
                e_wallet=request.form.get('e_wallet'),
                activity_type=request.form.get('activity_type'),
                province=request.form.get('province'),
                district=request.form.get('district'),
                # تصفير الأرصدة السيادية الثلاثة
                balance_yer=0.0, balance_sar=0.0, balance_usd=0.0
            )
            
            db.session.add(new_vendor)
            db.session.commit()
            return jsonify({"status": "success", "message": "تم تعميد المورد بنجاح وربطه بالهوية MAH-963"})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": f"فشل الحفظ: {str(e)}"}), 500

    return render_template('add_supplier.html', 
                           next_id=get_next_sovereign_id(), 
                           next_wallet=generate_vendor_wallet())

# --- 6. الإدارة والمراقبة المالية ---
@admin_bp.route('/suppliers')
@login_required
def manage_suppliers():
    suppliers_list = Vendor.query.all()
    return render_template('manage_suppliers.html', suppliers=suppliers_list)

@admin_bp.route('/withdraw-requests')
@login_required
def withdraw_requests():
    requests_list = WithdrawRequest.query.order_by(WithdrawRequest.id.desc()).all()
    return render_template('withdraw_requests.html', requests=requests_list)

# --- 7. تأمين الوصول ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and getattr(current_user, 'role', '') == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    return handle_admin_login()

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("تم تأمين النظام بنجاح", "info")
    return redirect(url_for('admin.login'))
