# coding: utf-8
# 📂 apps/admin_permissions/routes.py

from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
import secrets
import string
import os
from cryptography.fernet import Fernet
from sqlalchemy.exc import IntegrityError

from apps.extensions import db
from apps.models.admin_staff_db import AdminStaff
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.supplier_db import Supplier 

admin_permissions_bp = Blueprint('admin_permissions', __name__, template_folder='templates')

def is_admin():
    return current_user.is_authenticated and (getattr(current_user, 'role', '') in ['admin', 'Owner'])

def generate_random_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))

# --- [API] التحقق اللحظي ---
@admin_permissions_bp.route('/admin/permissions/check-user', methods=['GET'])
@login_required
def check_user():
    username = request.args.get('username', '')
    if len(username) < 3: return jsonify({'available': False})
    exists = AdminStaff.query.filter_by(username=username).first() or \
             SupplierStaff.query.filter_by(username=username).first()
    return jsonify({'available': exists is None})

@admin_permissions_bp.route('/admin/permissions/check-phone', methods=['GET'])
@login_required
def check_phone():
    phone = request.args.get('phone', '')
    staff_type = request.args.get('type', 'admin')
    if len(phone) != 9 or not phone.startswith('7'):
        return jsonify({'available': False})
    model = AdminStaff if staff_type == 'admin' else SupplierStaff
    exists = model.query.filter_by(phone=phone).first()
    return jsonify({'available': exists is None})

# --- عرض القائمة ---
@admin_permissions_bp.route('/admin/permissions/roles', methods=['GET'])
@login_required
def roles_list():
    if not is_admin(): return redirect(url_for('admin_dashboard.dashboard'))
    staff_type = request.args.get('type', 'admin')
    model = AdminStaff if staff_type == 'admin' else SupplierStaff
    staff_list = model.query.order_by(model.created_at.desc()).all()
    return render_template('admin/permissions.html', staff=staff_list, type_filter=staff_type, suppliers=Supplier.query.all())

# --- إضافة موظف جديد ---
@admin_permissions_bp.route('/admin/permissions/assign', methods=['POST'])
@login_required
def assign_permissions():
    if not is_admin(): return jsonify({'success': False, 'message': 'غير مصرح'})
    
    username = request.form.get('username')
    phone = request.form.get('phone')
    staff_type = request.form.get('type')
    supplier_id = request.form.get('supplier_id')
    
    if not phone or len(phone) != 9 or not phone.startswith('7'):
        return jsonify({'success': False, 'message': 'بيانات الهاتف غير صالحة'})
    
    model = AdminStaff if staff_type == 'admin' else SupplierStaff
    if model.query.filter_by(username=username).first() or model.query.filter_by(phone=phone).first():
        return jsonify({'success': False, 'message': 'الموظف موجود مسبقاً'})

    try:
        password = generate_random_password()
        enc_key = os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq=')
        fernet = Fernet(enc_key.encode())

        if staff_type == 'admin':
            new_staff = AdminStaff(username=username, role='worker')
            supplier_info = {'trade_name': 'إدارة مركزية', 'supplier_code': 'SYSTEM'}
        else:
            supplier = Supplier.query.get_or_404(int(supplier_id))
            new_staff = SupplierStaff(username=username, role='worker', supplier_id=supplier.id)
            supplier_info = {'trade_name': supplier.trade_name, 'supplier_code': supplier.supplier_code}

        new_staff.phone = phone
        new_staff._phone_enc = fernet.encrypt(str(phone).encode()).decode()
        
        if hasattr(new_staff, 'search_phone'):
            new_staff.search_phone = str(phone)[-9:]
            
        new_staff.set_password(password)
        db.session.add(new_staff)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'username': username, 
            'new_password': password,
            'store_name': supplier_info['trade_name'],
            'store_code': supplier_info['supplier_code']
        })
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'خطأ: اسم المستخدم أو الهاتف مستخدم من قبل'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f"خطأ غير متوقع: {str(e)}"})

# --- إدارة الحسابات (إعادة تعيين كلمة المرور) ---
@admin_permissions_bp.route('/admin/permissions/reset-password/<int:id>/<type>', methods=['GET'])
@login_required
def reset_password(id, type):
    if not is_admin(): return jsonify({'success': False, 'message': 'غير مصرح'})
    
    model = AdminStaff if type == 'admin' else SupplierStaff
    user = model.query.get_or_404(id)
    
    # جلب بيانات المتجر لإرسالها للواجهة
    if type == 'admin':
        store_name = 'إدارة مركزية'
        store_code = 'SYSTEM'
    else:
        store_name = user.supplier.trade_name if user.supplier else 'غير محدد'
        store_code = user.supplier.supplier_code if user.supplier else '---'
    
    new_pass = generate_random_password()
    user.set_password(new_pass)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'username': user.username, 
        'new_password': new_pass,
        'store_name': store_name,
        'store_code': store_code
    })

# --- تغيير حالة الحساب ---
@admin_permissions_bp.route('/admin/permissions/toggle-status/<int:id>/<type>', methods=['GET'])
@login_required
def toggle_status(id, type):
    if not is_admin(): return redirect(url_for('admin_dashboard.dashboard'))
    model = AdminStaff if type == 'admin' else SupplierStaff
    user = model.query.get_or_404(id)
    user.is_active = not user.is_active
    db.session.commit()
    return redirect(url_for('admin_permissions.roles_list', type=type))
