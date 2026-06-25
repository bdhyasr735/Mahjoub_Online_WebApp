# coding: utf-8
# 📂 apps/suppliers_dashboard/routes.py

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from apps.models.supplier_db import Supplier

# تعريف الـ Blueprint
dashboard_bp = Blueprint('suppliers_dashboard', __name__, template_folder='templates')

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """
    لوحة تحكم المورد - عرض مباشر بدون قيود إضافية
    """
    # إحصائيات افتراضية (يمكنك ربطها بالبيانات الحقيقية لاحقاً)
    supplier_stats = {
        'total_sales': '0.00',
        'pending_orders': 0
    }
    
    # عرض القالب المباشر
    return render_template('suppliers/dashboard.html', 
                           supplier_stats=supplier_stats)

@dashboard_bp.route('/')
@login_required
def index():
    """
    تحويل المسار الجذري للـ blueprint إلى لوحة التحكم
    """
    return redirect(url_for('suppliers_dashboard.dashboard'))
