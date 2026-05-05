import os
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import logout_user, login_required, current_user
from sqlalchemy import text
from datetime import datetime

# الاستيراد من الهيكلية المعتمدة للترسانة
from core.extensions import db 
from core.models.supplier import Supplier
from core.models.user import User

from . import admin_bp
from .auth import handle_admin_login

# --- 1. بروتوكول التحقق السيادي (حماية مركز القيادة) ---
def is_admin_sovereign():
    """ يضمن أن المؤسس علي محجوب فقط يمكنه الوصول. """
    return current_user.is_authenticated and getattr(current_user, 'role', '').lower() == 'admin'

# --- 2. بوابة الدخول (The Gateway) ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if is_admin_sovereign(): 
        return redirect(url_for('admin.admin_dashboard'))
    return handle_admin_login()

# --- 3. مركز القيادة (Dashboard) ---
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if not is_admin_sovereign():
        return redirect(url_for('admin.login'))
    
    try:
        suppliers_count = Supplier.query.count()
        users_count = User.query.count()
        
        try:
            from core.models.business import Order
            orders_count = Order.query.count()
        except Exception:
            orders_count = 0

        stats = {
            'suppliers_count': suppliers_count,
            'orders_count': orders_count,
            'users_count': users_count,
            'now': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return render_template('dashboard.html', **stats)
        
    except Exception as e:
        return render_template('dashboard.html', suppliers_count=0, orders_count=0, users_count=0, now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# --- 4. إدارة الموردين ---
@admin_bp.route('/manage-suppliers')
@login_required
def manage_suppliers():
    if not is_admin_sovereign(): 
        return redirect(url_for('admin.login'))
    
    try:
        suppliers = Supplier.query.order_by(Supplier.created_at.desc()).all()
        return render_template('manage_suppliers.html', suppliers=suppliers)
    except Exception as e:
        flash(f"خلل في الوصول لسجلات الموردين: {str(e)}", "danger")
        return redirect(url_for('admin.admin_dashboard'))

# --- 5. بروتوكول تعميد مورد جديد ---
@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if not is_admin_sovereign(): 
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        try:
            activity = request.form.get('activity_type')
            if activity == 'manual':
                activity = request.form.get('manual_activity')
            
            id_type = request.form.get('id_type')
            if id_type == 'manual':
                id_type = request.form.get('manual_id_type')

            new_supplier = Supplier(
                username=request.form.get('username'),
                password=request.form.get('password'),
                owner_name=request.form.get('owner_name'),
                trade_name=request.form.get('trade_name'),
                activity_type=activity,
                id_type=id_type,
                id_card_number=request.form.get('id_card_number'),
                phone=request.form.get('phone'),
                province=request.form.get('province'),
                district=request.form.get('district'),
                address_detail=request.form.get('address_detail'),
                e_wallet=request.form.get('e_wallet'),
                bank_name=request.form.get('bank_name') if request.form.get('bank_name') != 'manual' else request.form.get('manual_bank'),
                bank_acc=request.form.get('bank_acc'),
                status='active'
            )
            
            db.session.add(new_supplier)
            db.session.commit()
            
            if is_ajax:
                return jsonify({'status': 'success', 'message': f'تم تعميد المورد "{new_supplier.trade_name}" بنجاح.'})
            
            flash(f"✅ تم تفعيل المورد {new_supplier.trade_name} بنجاح", "success")
            return redirect(url_for('admin.manage_suppliers'))
            
        except Exception as e:
            db.session.rollback()
            if is_ajax:
                return jsonify({'status': 'error', 'message': str(e)}), 400
            flash(f"❌ فشل الإضافة: {str(e)}", "danger")

    last_s = Supplier.query.order_by(Supplier.id.desc()).first()
    next_id_val = (last_s.id + 1) if last_s else 1
    return render_template('add_supplier.html', next_id=f"SUP-{next_id_val:04d}", next_wallet=f"WAL-{next_id_val:06d}")

# --- 6. تسجيل الخروج الآمن (تم إصلاح الفاصلة هنا) ---
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("تم الخروج الآمن من نظام الإدارة", "info") # تم تغيير (،) إلى (,)
    return redirect(url_for('admin.login'))
