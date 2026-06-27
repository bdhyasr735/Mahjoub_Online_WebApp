# coding: utf-8
# 📂 apps/suppliers_dashboard/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, session, abort
from flask_login import login_required, current_user
from apps.models import Order 

# تعريف البلوبرينت
dashboard_bp = Blueprint(
    'suppliers_dashboard', 
    __name__, 
    template_folder='templates'
)

def supplier_required():
    """دالة مساعدة للتحقق من أن المستخدم مورد أو مسوق."""
    if session.get('user_type') != 'supplier':
        abort(403) # منع أي محاولة دخول لغير الموردين

@dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """لوحة التحكم الرئيسية للمورد."""
    supplier_required() # التحقق الأمني
    
    pending_orders_count = Order.query.filter_by(
        supplier_id=current_user.id, 
        status='pending'
    ).count()

    context = {
        'pending_orders_count': pending_orders_count,
    }
    
    return render_template('suppliers/dashboard.html', **context)

@dashboard_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    supplier_required() # التحقق الأمني
    flash("سيتم تفعيل خدمة السحب قريباً، يرجى التواصل مع الإدارة.", "info")
    return redirect(url_for('suppliers_dashboard.dashboard'))

@dashboard_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    supplier_required() # التحقق الأمني
    return render_template('suppliers/settings.html')
