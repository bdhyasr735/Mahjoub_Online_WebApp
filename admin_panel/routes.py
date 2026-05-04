# admin_panel/routes.py

import os
import re
import random
import string
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import text
from core import db 
from werkzeug.security import generate_password_hash
from . import admin_bp
from .auth import handle_admin_login

# --- 1. استيراد النماذج السيادية ---
try:
    from core.models.user import User
    from core.models.vendor import Vendor, WithdrawRequest
    try:
        from core.models.business import Order, Supplier
    except ImportError:
        Order = Supplier = None
except ImportError as e:
    print(f"❗ Import Warning: {e}")
    User = Vendor = WithdrawRequest = None

# --- 2. خدمات الهوية والمحافظ السيادية (الموحدة) ---
def get_sovereign_identity():
    """توليد الهوية الموحدة للمورد والمحفظة لضمان التطابق MAH-963X و W-MAH963X"""
    try:
        db.session.rollback()
        count = db.session.query(Vendor).count() if Vendor else 0
        next_number = count + 1
        return {
            'id': f"MAH-963{next_number}",
            'wallet': f"W-MAH963{next_number}"
        }
    except:
        rand = random.randint(100, 999)
        return {'id': f"MAH-963{rand}", 'wallet': f"W-MAH963{rand}"}

# --- 3. مسار الطوارئ (ترميم هيكل الترسانة) ---
@admin_bp.route('/force-repair-now')
def force_repair():
    try:
        db.session.rollback() 
        # إضافة الأعمدة الضرورية التي تسببت في الخطأ
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS supplier_id VARCHAR(50) UNIQUE;"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS e_wallet VARCHAR(100) UNIQUE;"))
        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'admin';"))
        
        db.create_all()
        db.session.commit()
        session['repair_done'] = True
        flash("تم ترميم هيكل الترسانة وتوحيد المعرفات بنجاح", "success")
        return redirect(url_for('admin.admin_dashboard'))
    except Exception as e:
        db.session.rollback()
        return f"Repair Error: {str(e)}"

# --- 4. لوحة التحكم ---
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    try:
        stats = {
            'suppliers_count': db.session.query(Vendor).count() if Vendor else 0,
            'pending_withdrawals': db.session.query(WithdrawRequest).filter_by(status='pending').count() if WithdrawRequest else 0,
            'orders_count': db.session.query(Order).count() if Order else 0
        }
        return render_template('dashboard.html', **stats, show_repair=not session.get('repair_done'))
    except Exception as e:
        db.session.rollback()
        return render_template('dashboard.html', suppliers_count=0, pending_withdrawals=0, orders_count=0, show_repair=True)

# --- 5. حوكمة الموردين (التعميد) ---
@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        try:
            db.session.rollback()
            username = request.form.get('username')
            password = request.form.get('password')
            
            if User.query.filter_by(username=username).first():
                return jsonify({"status": "error", "message": "اسم المستخدم موجود مسبقاً"}), 400

            # إنشاء المستخدم مع الحقل الصحيح password_hash
            new_user = User(
                username=username,
                password_hash=generate_password_hash(password),
                role='vendor'
            )
            db.session.add(new_user)
            db.session.flush() 

            # جلب البيانات وتخزين المورد
            new_vendor = Vendor(
                user_id=new_user.id,
                supplier_id=request.form.get('next_id'),
                trade_name=request.form.get('trade_name'),
                owner_name=request.form.get('owner_name'),
                phone=request.form.get('phone'),
                e_wallet=request.form.get('e_wallet'),
                activity_type=request.form.get('activity_type'),
                id_type=request.form.get('id_type'),
                id_card_number=request.form.get('id_card_number'),
                province=request.form.get('province'),
                district=request.form.get('district'),
                address_detail=request.form.get('address_detail'),
                bank_name=request.form.get('bank_name'),
                bank_acc=request.form.get('bank_acc'),
                fin_type=request.form.get('fin_type')
            )
            
            db.session.add(new_vendor)
            db.session.commit()
            return jsonify({"status": "success", "message": "تم تعميد المورد بنجاح"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500

    # التوليد عند فتح النموذج
    identity = get_sovereign_identity()
    return render_template('add_supplier.html', next_id=identity['id'], next_wallet=identity['wallet'])

# --- 6. الإدارة والوصول ---
@admin_bp.route('/suppliers')
@login_required
def manage_suppliers():
    suppliers_list = Vendor.query.all() if Vendor else []
    return render_template('manage_suppliers.html', suppliers=suppliers_list)

@admin_bp.route('/manage-wallets')
@login_required
def manage_wallets():
    suppliers_list = Vendor.query.all() if Vendor else []
    return render_template('wallets.html', suppliers=suppliers_list)

@admin_bp.route('/withdraw-requests')
@login_required
def withdraw_requests():
    requests_list = WithdrawRequest.query.order_by(WithdrawRequest.id.desc()).all() if WithdrawRequest else []
    return render_template('withdraw_requests.html', requests=requests_list)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and getattr(current_user, 'role', 'admin') == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    return handle_admin_login()

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))
