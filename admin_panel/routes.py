import os
import re
import random
import string
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import text
from core import db 

# --- استيراد النماذج ---
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

# --- الربط مع الخدمات ---
try:
    from services.wallet_service import generate_wallet_id
except ImportError:
    def generate_wallet_id(next_id=None):
        if next_id:
            return f"W-{next_id}"
        return f"W-MAH-{random.randint(9000, 9999)}"

from . import admin_bp
from .auth import handle_admin_login

def get_next_sovereign_id():
    try:
        db.session.rollback()
        count = db.session.query(Vendor).count() if Vendor else 0
        return f"MAH-963{count + 1}"
    except:
        return f"MAH-963{random.randint(1, 99)}"

# --- 1. مسار الطوارئ والترميم ---
@admin_bp.route('/force-repair-now')
def force_repair():
    report = []
    try:
        db.session.rollback() 
        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'admin';"))
        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active_account BOOLEAN DEFAULT TRUE;"))
        
        legacy_columns = ['vendor_uid', 'username', 'email', 'status']
        for col in legacy_columns:
            db.session.execute(text(f"ALTER TABLE vendors ADD COLUMN IF NOT EXISTS {col} VARCHAR(255);"))
            db.session.execute(text(f"ALTER TABLE vendors ALTER COLUMN {col} DROP NOT NULL;"))

        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS balance_yer FLOAT DEFAULT 0.0;"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS balance_sar FLOAT DEFAULT 0.0;"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS balance_usd FLOAT DEFAULT 0.0;"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS user_id INTEGER;"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS e_wallet VARCHAR(100);"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS province VARCHAR(100);"))
        db.session.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS district VARCHAR(100);"))
        
        db.session.commit()
        session['repair_done'] = True
        flash("تم ترميم القاعدة بنجاح", "success")
        return redirect(url_for('admin.admin_dashboard'))
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}"

# --- 2. لوحة التحكم ---
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    try:
        db.session.rollback()
        stats = {'suppliers_count': 0, 'pending_withdrawals': 0, 'orders_count': 0}
        show_repair = not session.get('repair_done', False)

        if Vendor:
            stats['suppliers_count'] = db.session.query(Vendor).count()
        if WithdrawRequest:
            stats['pending_withdrawals'] = db.session.query(WithdrawRequest).filter_by(status='pending').count()
        
        return render_template('dashboard.html', **stats, show_repair=show_repair)
    except Exception as e:
        db.session.rollback()
        return render_template('dashboard.html', suppliers_count=0, pending_withdrawals=0, show_repair=True)

# --- 3. حوكمة الموردين ---
@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        try:
            db.session.rollback()
            username = request.form.get('username')
            password = request.form.get('password')
            received_id = request.form.get('next_id') or get_next_sovereign_id()
            received_wallet = request.form.get('e_wallet') or generate_wallet_id(received_id)

            if User.query.filter_by(username=username).first():
                return jsonify({"status": "error", "message": "المستخدم موجود"})

            new_user = User(username=username, role='vendor')
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush() 

            new_vendor = Vendor(
                user_id=new_user.id, vendor_uid=received_id,
                owner_name=request.form.get('owner_name'), trade_name=request.form.get('trade_name'),
                phone=request.form.get('phone'), e_wallet=received_wallet,
                balance_yer=0.0, balance_sar=0.0, balance_usd=0.0,
                province=request.form.get('province'), district=request.form.get('district')
            )
            db.session.add(new_vendor)
            db.session.commit()
            return jsonify({"status": "success", "message": "تم بنجاح"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
    return render_template('add_supplier.html')

@admin_bp.route('/suppliers')
@login_required
def manage_suppliers():
    suppliers_list = Vendor.query.all() if Vendor else []
    return render_template('manage_suppliers.html', suppliers=suppliers_list)

# --- 4. المسارات المفقودة (تمت إضافتها لمنع الانهيار) ---

@admin_bp.route('/withdraw-requests')
@login_required
def withdraw_requests():
    # هذا المسار تطلبه القوالب لمنع Error 500
    return render_template('manage_suppliers.html', suppliers=[]) 

@admin_bp.route('/manage-wallets')
@login_required
def manage_wallets():
    # هذا المسار تطلبه القوالب لمنع Error 500
    return render_template('manage_suppliers.html', suppliers=[])

# --- 5. الهوية والجلسات ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and getattr(current_user, 'role', 'admin') == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    return handle_admin_login()

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('تم الخروج الآمن.', 'info')
    return redirect(url_for('admin.login'))
