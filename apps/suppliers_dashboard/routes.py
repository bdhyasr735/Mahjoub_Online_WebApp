# coding: utf-8
# 📂 apps/suppliers_dashboard/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

# تعريف الـ Blueprint
dashboard_bp = Blueprint(
    'suppliers_dashboard', 
    __name__, 
    template_folder='templates'
)

@dashboard_bp.route('/')
@login_required
def index():
    """
    نقطة الدخول للمسار الجذري للمورد (/suppliers/).
    يتم التحقق من وجود المحفظة قبل التوجيه للوحة التحكم.
    """
    if hasattr(current_user, 'wallet') and current_user.wallet is not None:
        return redirect(url_for('suppliers_dashboard.dashboard'))
    
    return "عذراً، هذا القسم مخصص للموردين فقط."

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """
    لوحة تحكم المورد: تعرض الإحصائيات الحية.
    """
    # 1. التحقق من صلاحية الوصول (مورد + محفظة)
    if not hasattr(current_user, 'wallet') or current_user.wallet is None:
        return redirect(url_for('suppliers_dashboard.index'))

    # 2. جلب كائن المحفظة
    wallet = current_user.wallet 
    
    # 3. حساب الطلبات قيد التنفيذ
    pending_orders_count = 0
    if hasattr(current_user, 'orders') and current_user.orders:
        pending_orders_count = len([o for o in current_user.orders if o.status == 'pending'])
    
    # 4. حساب إجمالي المبيعات المكتملة
    total_sales = 0.00
    if hasattr(current_user, 'financials') and current_user.financials:
        total_sales = sum(float(f.amount) for f in current_user.financials if f.status == 'completed')

    # 5. تمرير البيانات للقالب
    return render_template(
        'suppliers/dashboard.html', 
        wallet=wallet,
        pending_orders_count=pending_orders_count,
        total_sales=total_sales
    )

@dashboard_bp.route('/settings')
@login_required
def settings():
    """
    صفحة إعدادات المتجر للمورد.
    """
    return render_template('suppliers/settings.html')
