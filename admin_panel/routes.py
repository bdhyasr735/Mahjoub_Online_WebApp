import os
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import logout_user, login_required, current_user
from sqlalchemy import text

# الاستيراد من الهيكلية المعتمدة
from core.extensions import db 
from core.models.supplier import Supplier
from core.models.user import User

from . import admin_bp
from .auth import handle_admin_login

# --- 1. بروتوكول التحقق السيادي (حماية مركز القيادة) ---
def is_admin_sovereign():
    """ يضمن أن علي محجوب فقط يمكنه الوصول. """
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
        total_users = User.query.count()
        
        try:
            from core.models.business import Order
            total_orders = Order.query.count()
        except Exception:
            total_orders = 0

        stats = {
            'suppliers_count': suppliers_count,
            'orders_count': total_orders,
            'users_count': total_users,
            'pending_withdrawals': 0 
        }
        return render_template('dashboard.html', **stats)
    except Exception as e:
        print(f"⚠️ Dashboard Error: {str(e)}")
        return render_template('dashboard.html', suppliers_count=0, orders_count=0, users_count=0, pending_withdrawals=0)

# --- 4. إضافة مورد جديد (إصلاح بروتوكول التعميد) ---
@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if not is_admin_sovereign(): 
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        try:
            # 1. استخراج بيانات الدخول والنشاط
            username = request.form.get('username')
            password = request.form.get('password')
            activity = request.form.get('activity_type')
            if activity == 'manual':
                activity = request.form.get('manual_activity')

            # 2. استخراج بيانات الهوية والتوثيق
            owner_name = request.form.get('owner_name')
            trade_name = request.form.get('trade_name')
            id_type = request.form.get('id_type')
            if id_type == 'manual':
                id_type = request.form.get('manual_id_type')
            id_card_number = request.form.get('id_card_number')

            # 3. استخراج البيانات الجغرافية (إصلاح خطأ location)
            province = request.form.get('province')
            district = request.form.get('district')
            address_detail = request.form.get('address_detail')
            phone = request.form.get('phone')

            # 4. استخراج بيانات الربط المالي
            e_wallet = request.form.get('e_wallet')
            bank_name = request.form.get('bank_name')
            if bank_name == 'manual':
                bank_name = request.form.get('manual_bank')
            bank_acc = request.form.get('bank_acc')

            # --- إنشاء سجل المورد الجديد وفقاً لهيكل الترسانة المحدث ---
            new_supplier = Supplier(
                username=username,
                password=password,
                owner_name=owner_name,
                trade_name=trade_name,
                activity_type=activity,
                id_type=id_type,
                id_card_number=id_card_number,
                phone=phone,
                province=province,      # الحقل الصحيح بدلاً من location
                district=district,      # الحقل الصحيح بدلاً من location
                address_detail=address_detail, # الحقل الصحيح بدلاً من location
                e_wallet=e_wallet,
                bank_name=bank_name,
                bank_acc=bank_acc,
                status='active'
            )
            
            db.session.add(new_supplier)
            db.session.commit()
            
            if is_ajax:
                return jsonify({
                    'status': 'success',
                    'message': f'تم تعميد المورد "{trade_name}" بنجاح في المنظومة.'
                })
            
            flash(f"✅ تم تفعيل المورد {trade_name} بنجاح", "success")
            return redirect(url_for('admin.manage_suppliers'))
            
        except Exception as e:
            db.session.rollback()
            error_msg = f"❌ فشل بروتوكول الإضافة: {str(e)}"
            if is_ajax:
                return jsonify({'status': 'error', 'message': error_msg}), 400
            flash(error_msg, "danger")

    # حساب المعرفات التلقائية للعرض
    last_s = Supplier.query.order_by(Supplier.id.desc()).first()
    next_id_num = (last_s.id + 1) if last_s else 1
    next_id = f"SUP-{next_id_num:04d}"
    next_wallet = f"WAL-{next_id_num:06d}"

    return render_template('add_supplier.html', next_id=next_id, next_wallet=next_wallet)

# --- 5. إدارة الموردين ---
@admin_bp.route('/manage-suppliers')
@login_required
def manage_suppliers():
    if not is_admin_sovereign(): 
        return redirect(url_for('admin.login'))
    
    try:
        suppliers = Supplier.query.order_by(Supplier.created_at.desc()).all()
        return render_template('manage_suppliers.html', suppliers=suppliers)
    except Exception as e:
        flash(f"خلل في الوصول للموردين: {str(e)}", "danger")
        return redirect(url_for('admin.admin_dashboard'))

# --- 6. إنهاء الجلسة ---
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("تم الخروج الآمن من نظام الإدارة", "info")
    return redirect(url_for('admin.login'))
