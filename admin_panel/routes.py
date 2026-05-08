import os
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import logout_user, login_required, current_user
from sqlalchemy import or_
from datetime import datetime
from functools import wraps

# الاستيراد من الهيكلية المعتمدة لترسانة محجوب أونلاين
from core.extensions import db 
from core.models.supplier import Supplier
from core.models.user import User

from . import admin_bp
from .auth import handle_admin_login

# --- 1. بروتوكول التحقق السيادي ---
def is_admin_sovereign():
    """ يضمن أن المؤسس علي محجوب فقط يمكنه الوصول. """
    return current_user.is_authenticated and getattr(current_user, 'role', '').lower() == 'admin'

def admin_api_required(f):
    """ تأمين الـ APIs لمنع الدخول غير المصرح به """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_sovereign():
            return jsonify({"status": "error", "message": "Access Denied: Sovereign Auth Required"}), 403
        return f(*args, **kwargs)
    return decorated_function

# --- 2. بوابة الدخول ---
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
        # جلب الإحصائيات مع حماية ضد فشل الجداول
        users_count = User.query.count() if User else 1
        suppliers_count = Supplier.query.count() if Supplier else 0
        
        stats = {
            'suppliers_count': suppliers_count,
            'users_count': users_count,
            'now': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # جلب الطلبات إن وجدت في الموديل
        try:
            from core.models.business import Order
            stats['orders_count'] = Order.query.count()
        except:
            stats['orders_count'] = 0

        return render_template('dashboard.html', **stats)
    except Exception as e:
        # في حال حدوث أي خطأ فني، يتم عرض صفحة آمنة
        return render_template('dashboard.html', users_count=1, suppliers_count=0, orders_count=0, now="إيقاع النظام مستقر")

# --- 4. إدارة الموردين (الكيانات المعتمدة) ---
@admin_bp.route('/manage-suppliers')
@login_required
def manage_suppliers(): # تم توحيد الاسم ليتوافق مع url_for في القوالب
    """ عرض قائمة الكيانات السيادية وإدارتها """
    if not is_admin_sovereign():
        return redirect(url_for('admin.login'))
    
    try:
        all_suppliers = Supplier.query.order_by(Supplier.id.desc()).all()
    except:
        all_suppliers = []
    return render_template('manage_suppliers.html', suppliers=all_suppliers)

# --- 5. تعميد مورد جديد ---
@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_supplier(): # هذا هو الـ Endpoint الذي كان يسبب BuildError في Railway
    if not is_admin_sovereign(): 
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        try:
            new_supplier = Supplier(
                username=request.form.get('username'),
                owner_name=request.form.get('owner_name'),
                trade_name=request.form.get('trade_name'),
                phone=request.form.get('phone'),
                province=request.form.get('province'),
                district=request.form.get('district'),
                status='active'
            )
            # تعيين كلمة المرور الافتراضية
            new_supplier.set_password(request.form.get('password', '123456'))
            
            db.session.add(new_supplier)
            db.session.flush() 
            
            # نقش المعرف الخاص WAL_MAH إذا كانت الدالة موجودة في الموديل
            if hasattr(new_supplier, 'mint_sovereign_id'):
                new_supplier.mint_sovereign_id()
                
            db.session.commit()
            
            if is_ajax: 
                return jsonify({'status': 'success', 'message': 'تم التعميد بنجاح'})
            flash("تم إضافة المورد الجديد للترسانة بنجاح", "success")
            return redirect(url_for('admin.manage_suppliers'))
            
        except Exception as e:
            db.session.rollback()
            if is_ajax: return jsonify({'status': 'error', 'message': str(e)}), 400
            flash(f"عطل في بروتوكول الإضافة: {str(e)}", "danger")

    return render_template('add_supplier.html')

# --- 6. بروتوكولات الـ API السيادية (التحكم الفوري) ---

@admin_bp.route('/api/supplier-details/<int:sup_id>')
@admin_api_required
def api_supplier_details(sup_id):
    supplier = Supplier.query.get_or_404(sup_id)
    return jsonify({
        "id": supplier.id,
        "owner_name": supplier.owner_name,
        "trade_name": supplier.trade_name,
        "phone": supplier.phone,
        "e_wallet": getattr(supplier, 'e_wallet', f"WAL_MAH_{supplier.id}"),
        "province": supplier.province,
        "district": supplier.district,
        "balance_yer": float(getattr(supplier, 'balance_yer', 0)),
        "status": supplier.status
    })

@admin_bp.route('/api/update-supplier-password/<int:sup_id>', methods=['POST'])
@admin_api_required
def update_supplier_password(sup_id):
    supplier = Supplier.query.get_or_404(sup_id)
    data = request.get_json()
    new_pass = data.get('password')
    
    if new_pass and len(new_pass) >= 6:
        supplier.set_password(new_pass)
        db.session.commit()
        return jsonify({"status": "success", "message": "تم تحديث كلمة المرور بنجاح"})
    return jsonify({"status": "error", "message": "كلمة المرور قصيرة جداً"}), 400

@admin_bp.route('/api/toggle-supplier-status/<int:sup_id>', methods=['POST'])
@admin_api_required
def toggle_supplier_status(sup_id):
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
    try:
        supplier = Supplier.query.get_or_404(sup_id)
        db.session.delete(supplier)
        db.session.commit()
        return jsonify({"status": "success", "message": "تم شطب الكيان بنجاح"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 7. إنهاء الجلسة الآمنة ---
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("تم إنهاء الجلسة السيادية بنجاح. النظام في وضع الاستعداد.", "info")
    return redirect(url_for('admin.login'))
