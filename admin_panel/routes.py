import os
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import logout_user, login_required, current_user
from sqlalchemy import or_, cast, String
from datetime import datetime
from functools import wraps

# الاستيراد من الهيكلية المعتمدة لترسانة محجوب أونلاين
from core.extensions import db 
from core.models.supplier import Supplier
from core.models.user import User

from . import admin_bp
from .auth import handle_admin_login

# --- 1. بروتوكول التحقق السيادي (حماية مركز القيادة) ---
def is_admin_sovereign():
    """ يضمن أن المؤسس علي محجوب فقط يمكنه الوصول. """
    return current_user.is_authenticated and getattr(current_user, 'role', '').lower() == 'admin'

def admin_api_required(f):
    """ ديكوريتور لتأمين طلبات الـ API ومنع رسائل تسجيل الدخول المزعجة """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_sovereign():
            return jsonify({"status": "error", "message": "Access Denied: Sovereign Auth Required"}), 403
        return f(*args, **kwargs)
    return decorated_function

# --- 2. بوابة الدخول (The Gateway) ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if is_admin_sovereign(): 
        return redirect(url_for('admin.admin_dashboard'))
    return handle_admin_login()

# --- 3. مركز القيادة الإحصائي (Dashboard) ---
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if not is_admin_sovereign():
        return redirect(url_for('admin.login'))
    
    try:
        # جلب البيانات الحقيقية لعرضها في الدشبرد
        stats = {
            'suppliers_count': Supplier.query.count(),
            'users_count': User.query.count(),
            'now': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        # محاولة جلب الطلبات إن وجدت
        try:
            from core.models.business import Order
            stats['orders_count'] = Order.query.count()
        except:
            stats['orders_count'] = 0

        return render_template('dashboard.html', **stats)
    except Exception as e:
        return render_template('dashboard.html', suppliers_count=0, now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# --- 4. إدارة الموردين (قائمة الكيانات المعتمدة) ---
@admin_bp.route('/manage-suppliers')
@login_required
def admin_manage_suppliers():
    if not is_admin_sovereign():
        return redirect(url_for('admin.login'))
    
    all_suppliers = Supplier.query.order_by(Supplier.id.desc()).all()
    return render_template('manage_suppliers.html', suppliers=all_suppliers)

# --- 5. بروتوكولات الـ API السيادية (التحكم الفوري) ---

@admin_bp.route('/api/supplier-details/<int:sup_id>')
@admin_api_required
def api_supplier_details(sup_id):
    """ جلب تفاصيل المورد للوحة الجانبية """
    supplier = Supplier.query.get_or_404(sup_id)
    return jsonify(supplier.to_dict())

@admin_bp.route('/api/toggle-supplier-status/<int:sup_id>', methods=['POST'])
@admin_api_required
def toggle_supplier_status(sup_id):
    """ تفعيل أو تعليق نشاط المورد """
    supplier = Supplier.query.get_or_404(sup_id)
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status in ['active', 'suspended']:
        supplier.status = new_status
        db.session.commit()
        return jsonify({"status": "success", "message": f"تم تحديث حالة الكيان إلى {new_status}"})
    return jsonify({"status": "error", "message": "حالة غير صالحة"}), 400

@admin_bp.route('/api/delete-supplier/<int:sup_id>', methods=['DELETE'])
@admin_api_required
def delete_supplier(sup_id):
    """ شطب الكيان نهائياً من الترسانة """
    try:
        supplier = Supplier.query.get_or_404(sup_id)
        db.session.delete(supplier)
        db.session.commit()
        return jsonify({"status": "success", "message": "تم شطب الكيان بنجاح"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 6. تعميد مورد جديد (The Creation Protocol) ---
@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if not is_admin_sovereign(): 
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        try:
            new_supplier = Supplier(
                username=request.form.get('username'),
                password=request.form.get('password', '123456'),
                owner_name=request.form.get('owner_name'),
                trade_name=request.form.get('trade_name'),
                phone=request.form.get('phone'),
                province=request.form.get('province'),
                district=request.form.get('district'),
                status='active'
            )
            db.session.add(new_supplier)
            db.session.flush() 
            new_supplier.mint_sovereign_id() # توليد المعرف WAL_MAH_XXXX
            db.session.commit()
            
            if is_ajax: 
                return jsonify({'status': 'success', 'message': 'تم التعميد بنجاح'})
            return redirect(url_for('admin.admin_manage_suppliers'))
            
        except Exception as e:
            db.session.rollback()
            if is_ajax: return jsonify({'status': 'error', 'message': str(e)}), 400
            flash(f"خطأ: {str(e)}", "danger")

    return render_template('add_supplier.html')

# --- 7. إنهاء الجلسة الآمنة ---
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("تم إنهاء الجلسة السيادية بنجاح", "info")
    return redirect(url_for('admin.login'))
