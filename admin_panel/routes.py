# admin_panel/routes.py

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

# --- 1. استيراد النماذج السيادية (مع مواءمة المسميات الجديدة) ---
try:
    from core.models.user import User
    # تم تغيير الاستيراد هنا ليتوافق مع وجود كلاس Supplier داخل ملف vendor.py
    from core.models.vendor import Supplier, WithdrawRequest
    try:
        from core.models.business import Order
    except ImportError:
        Order = None
except ImportError as e:
    print(f"❗ Import Warning: {e}")
    User = Supplier = WithdrawRequest = Order = None

# --- 2. خدمات الهوية والمحافظ السيادية ---
def get_sovereign_identity():
    """توليد الهوية الموحدة MAH-963X لضمان عدم تكرار المعرفات"""
    try:
        db.session.rollback()
        # استخدام Supplier بدلاً من Vendor
        count = db.session.query(Supplier).count() if Supplier else 0
        next_number = count + 1
        return {
            'id': f"MAH-963{next_number}",
            'wallet': f"W-MAH963{next_number}"
        }
    except Exception:
        rand = random.randint(1000, 9999)
        return {'id': f"MAH-963{rand}", 'wallet': f"W-MAH963{rand}"}

# --- 3. مسار الطوارئ (الترميم الهيكلي) ---
@admin_bp.route('/force-repair-now')
@login_required
def force_repair():
    if getattr(current_user, 'role', '') != 'admin':
        return "Unauthorized", 403
        
    try:
        db.session.rollback() 
        
        # 1. تحديث جدول الموردين (vendors) للسماح بكلمات مرور فارغة
        db.session.execute(text("ALTER TABLE vendors ALTER COLUMN password DROP NOT NULL;"))
        
        # 2. ضمان وجود الأعمدة السيادية وتصحيح القيود
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS supplier_id VARCHAR(50) UNIQUE;"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS e_wallet VARCHAR(100) UNIQUE;"))
        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'vendor';"))
        
        db.session.commit()
        session['repair_done'] = True
        flash("تم ترميم هيكل الترسانة وتوحيد المعرفات السيادية بنجاح", "success")
        return redirect(url_for('admin.admin_dashboard'))
    except Exception as e:
        db.session.rollback()
        return f"Database Repair Critical Error: {str(e)}"

# --- 4. لوحة التحكم (مركز المراقبة العليا) ---
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if getattr(current_user, 'role', '') != 'admin':
        flash("عذراً، هذه المنطقة مخصصة للرقابة العليا فقط", "danger")
        return redirect(url_for('main.index'))

    try:
        stats = {
            'suppliers_count': db.session.query(Supplier).count() if Supplier else 0,
            'pending_withdrawals': db.session.query(WithdrawRequest).filter_by(status='pending').count() if WithdrawRequest else 0,
            'orders_count': db.session.query(Order).count() if Order else 0
        }
        return render_template('dashboard.html', **stats, show_repair=not session.get('repair_done'))
    except Exception as e:
        db.session.rollback()
        return render_template('dashboard.html', suppliers_count=0, pending_withdrawals=0, orders_count=0, show_repair=True)

# --- 5. حوكمة الموردين (التعميد والربط) ---
@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        try:
            db.session.rollback()
            username = request.form.get('username')
            password = request.form.get('password')
            
            if User.query.filter_by(username=username).first():
                return jsonify({"status": "error", "message": "اسم المستخدم مسجل مسبقاً في النظام"}), 400

            # إنشاء حساب المستخدم الأساسي
            new_user = User(
                username=username,
                password_hash=generate_password_hash(password),
                role='vendor'
            )
            db.session.add(new_user)
            db.session.flush() 

            # إنشاء بروفايل المورد المرتبط (Supplier)
            new_supplier = Supplier(
                user_id=new_user.id,
                supplier_id=request.form.get('next_id'),
                trade_name=request.form.get('trade_name'),
                owner_name=request.form.get('owner_name'),
                phone=request.form.get('phone'),
                e_wallet=request.form.get('e_wallet'),
                activity_type=request.form.get('activity_type'),
                province=request.form.get('province'),
                district=request.form.get('district'),
                balance_yer=0.0, balance_sar=0.0, balance_usd=0.0
            )
            
            db.session.add(new_supplier)
            db.session.commit()
            return jsonify({"status": "success", "message": "تم تعميد المورد بنجاح وربط المحفظة السيادية"})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": f"فشل في بروتوكول التعميد: {str(e)}"}), 500

    identity = get_sovereign_identity()
    return render_template('add_supplier.html', 
                           next_id=identity['id'], 
                           next_wallet=identity['wallet'])

# --- 6. الإدارة المالية والمراقبة الميدانية ---
@admin_bp.route('/suppliers')
@login_required
def manage_suppliers():
    try:
        # الربط مع الحساب (User) عبر العلاقة المعرفة في الموديل
        suppliers_list = db.session.query(Supplier).options(joinedload(Supplier.user)).all() if Supplier else []
        return render_template('manage_suppliers.html', suppliers=suppliers_list)
    except Exception as e:
        db.session.rollback()
        flash(f"فشل استعراض الموردين: {str(e)}", "danger")
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/manage-wallets')
@login_required
def manage_wallets():
    try:
        suppliers_list = Supplier.query.all() if Supplier else []
        return render_template('wallets.html', suppliers=suppliers_list)
    except Exception as e:
        flash(f"خطأ في الوصول للهندسة المالية: {str(e)}", "danger")
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/withdraw-requests')
@login_required
def withdraw_requests():
    try:
        requests_list = WithdrawRequest.query.order_by(WithdrawRequest.id.desc()).all() if WithdrawRequest else []
        return render_template('withdraw_requests.html', requests=requests_list)
    except Exception as e:
        flash(f"خطأ في جلب طلبات السحب: {str(e)}", "danger")
        return redirect(url_for('admin.admin_dashboard'))

# --- 7. بوابة الوصول السيادية ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and getattr(current_user, 'role', '') == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    return handle_admin_login()

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("تم إنهاء الجلسة السيادية وتأمين النظام", "info")
    return redirect(url_for('admin.login'))
