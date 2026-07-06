# coding: utf-8
# 📂 apps/suppliers_dashboard/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, session, abort, request
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from apps.extensions import db  
from apps.models.orders_db import Order 
from apps.models.supplier_db import Supplier

# تم تعديل اسم الـ Blueprint واسم المتغير ليتوافق مع النظام الديناميكي
suppliers_dashboard_bp = Blueprint('suppliers_dashboard', __name__, template_folder='templates')

def full_access_required():
    """التحقق من صلاحيات الوصول للمورد"""
    if session.get('user_type') == 'supplier':
        return
    if session.get('user_type') == 'staff' and getattr(current_user, 'role', None) == 'owner':
        return
    abort(403)

@suppliers_dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """لوحة التحكم الرئيسية للمورد"""
    user_type = session.get('user_type')
    
    if user_type == 'supplier':
        s_id = getattr(current_user, 'id', None)
    elif user_type == 'staff':
        s_id = getattr(current_user, 'supplier_id', None)
    else:
        s_id = None

    if not s_id:
        abort(403, description="لا يمكن تحديد هوية المورد.")

    supplier = Supplier.query.options(joinedload(Supplier.wallet)).get(s_id)
    
    pending_orders_count = Order.query.filter_by(
        supplier_id=s_id, 
        status='pending'
    ).count()

    return render_template('suppliers/dashboard.html', 
                           current_user=supplier, 
                           pending_orders_count=pending_orders_count)

@suppliers_dashboard_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    full_access_required() 
    flash("سيتم تفعيل خدمة السحب قريباً، يرجى التواصل مع الإدارة.", "info")
    return redirect(url_for('suppliers_dashboard.dashboard'))

@suppliers_dashboard_bp.route('/settings', methods=['GET'])
@login_required
def settings():
    full_access_required() 
    
    user_type = session.get('user_type')
    s_id = current_user.id if user_type == 'supplier' else getattr(current_user, 'supplier_id', None)
    
    supplier_data = Supplier.query.options(
        joinedload(Supplier.supplier_profile),
        joinedload(Supplier.wallet)
    ).get(s_id)
    
    if not supplier_data:
        abort(404)
        
    return render_template('suppliers/settings.html', current_user=supplier_data)

@suppliers_dashboard_bp.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    full_access_required()
    
    target = current_user if session.get('user_type') == 'supplier' else getattr(current_user, 'supplier', None)
    if not target or not hasattr(target, 'supplier_profile'):
        flash("خطأ في البيانات.", "danger")
        return redirect(url_for('suppliers_dashboard.settings'))
        
    profile = target.supplier_profile
    profile.owner_name = request.form.get('owner_name')
    profile.email = request.form.get('email')
    profile.phone_secondary = request.form.get('secondary_phone')
    profile.governorate = request.form.get('governorate')
    profile.city = request.form.get('city')
    profile.address = request.form.get('address')
    
    db.session.commit()
    flash("تم تحديث البيانات بنجاح!", "success")
    return redirect(url_for('suppliers_dashboard.settings'))

@suppliers_dashboard_bp.route('/settings/update-password', methods=['POST'])
@login_required
def update_password():
    full_access_required()
    if current_user.check_password(request.form.get('old_password')):
        current_user.set_password(request.form.get('new_password'))
        db.session.commit()
        flash("تم تغيير كلمة المرور بنجاح!", "success")
    else:
        flash("كلمة المرور الحالية غير صحيحة.", "danger")
    return redirect(url_for('suppliers_dashboard.settings'))
