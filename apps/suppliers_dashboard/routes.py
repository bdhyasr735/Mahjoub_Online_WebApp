# coding: utf-8
# 📂 apps/suppliers_dashboard/routes.py

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

# تعريف الـ Blueprint
dashboard_bp = Blueprint(
    'suppliers_dashboard', 
    __name__, 
    template_folder='templates'
)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """
    لوحة تحكم المورد: 
    تقوم بجلب البيانات الحقيقية للمورد (المحفظة، الطلبات، الإحصائيات) وتمريرها للقالب.
    """
    
    # 1. جلب بيانات المحفظة (التي تحتوي على العملات الثلاث: YER, USD, SAR)
    # ملاحظة: تم التأكد من ربط العلاقة في Supplier باسم 'wallet'
    wallet = current_user.wallet 
    
    # 2. حساب الطلبات قيد التنفيذ (Pending)
    pending_orders_count = 0
    if hasattr(current_user, 'orders') and current_user.orders:
        pending_orders_count = len([o for o in current_user.orders if o.status == 'pending'])
    
    # 3. حساب إجمالي المبيعات المكتملة
    total_sales = 0.00
    if hasattr(current_user, 'financials') and current_user.financials:
        # نفترض أن كل عملية مالية لها حقل amount
        total_sales = sum(float(f.amount) for f in current_user.financials if f.status == 'completed')

    # 4. إعداد الإحصائيات للواجهة
    supplier_stats = {
        'total_sales': "{:,.2f}".format(total_sales),
        'pending_orders': pending_orders_count
    }
    
    # تمرير البيانات:
    # - wallet: كائن المحفظة للوصول لـ balance_yer, balance_usd, balance_sar
    # - supplier_stats: للإحصائيات العامة
    # - pending_orders_count: للبطاقة الديناميكية
    return render_template(
        'suppliers/dashboard.html', 
        wallet=wallet,
        supplier_stats=supplier_stats,
        pending_orders_count=pending_orders_count
    )

@dashboard_bp.route('/settings')
@login_required
def settings():
    """صفحة إعدادات المتجر"""
    return render_template('suppliers/settings.html')

@dashboard_bp.route('/')
@login_required
def index():
    """توجيه تلقائي للوحة التحكم"""
    return redirect(url_for('suppliers_dashboard.dashboard'))
