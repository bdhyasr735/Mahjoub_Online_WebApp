# admin_panel/routes.py
from flask import Blueprint, redirect, url_for, render_template, request, flash
from flask_login import login_required, logout_user
from core import db
from core.models.user import User
from core.models.supplier import Supplier
from datetime import datetime

# استيراد المحركات (Logic)
from .auth import login_view 
from .suppliers_logic import SupplierLogic

# تعريف البلوبرنت
admin_bp = Blueprint('admin', __name__, template_folder='templates')

# ==========================================
# 1. بوابة الدخول (The Security Gate)
# ==========================================

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """توجيه طلب الدخول إلى المحرك المختص في auth.py"""
    return login_view()

# ==========================================
# 2. غرفة القيادة (The Dashboard)
# ==========================================

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """عرض لوحة التحكم مع إحصائيات الترسانة الرقمية"""
    data = {
        'users_count': User.query.count(),
        'suppliers_count': Supplier.query.count(),
        'orders_count': 0,  # سيتم ربطه لاحقاً بجدول الطلبات
        'total_yer': db.session.query(db.func.sum(Supplier.balance_yer)).scalar() or 0.0,
        'total_sar': db.session.query(db.func.sum(Supplier.balance_sar)).scalar() or 0.0,
        'total_usd': db.session.query(db.func.sum(Supplier.balance_usd)).scalar() or 0.0,
        'now': datetime.now()
    }
    return render_template('admin/dashboard.html', **data)

# ==========================================
# 3. حوكمة الموردين (Supplier Governance)
# ==========================================

@admin_bp.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    """شاشة تعميد مورد جديد"""
    if request.method == 'POST':
        # تمرير بيانات الفورم لمحرك المنطق
        success, message = SupplierLogic.register_supplier(request.form)
        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('admin.manage_suppliers'))
            
    # توليد المعرف القادم لإظهاره في الواجهة الملكية
    next_id = SupplierLogic.get_next_id()
    return render_template('admin/add_supplier.html', next_id=next_id)

@admin_bp.route('/suppliers
