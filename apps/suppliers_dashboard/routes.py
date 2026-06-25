# coding: utf-8
# 📂 apps/suppliers_dashboard/routes.py

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

# تعريف الـ Blueprint مع تحديد مسار مجلد القوالب
# تذكر: Flask يبحث عن القوالب انطلاقاً من المجلد المحدد (templates)
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
    تقوم بجلب البيانات الحقيقية للمورد من قاعدة البيانات وتمريرها للقالب.
    """
    
    # 1. حساب الطلبات قيد التنفيذ (Pending)
    pending_orders_count = 0
    if hasattr(current_user, 'orders') and current_user.orders:
        pending_orders_count = len([o for o in current_user.orders if o.status == 'pending'])
    
    # 2. حساب إجمالي المبيعات المكتملة (Completed)
    total_sales = 0.00
    if hasattr(current_user, 'financials') and current_user.financials:
        total_sales = sum(float(f.amount) for f in current_user.financials if f.status == 'completed')

    # 3. إعداد مصفوفة الإحصائيات للواجهة
    supplier_stats = {
        'total_sales': "{:,.2f}".format(total_sales),
        'pending_orders': pending_orders_count
    }
    
    # 4. تمرير البيانات لقالب dashboard.html الموجود في المسار:
    # templates/suppliers/dashboard.html
    return render_template(
        'suppliers/dashboard.html', 
        supplier_stats=supplier_stats
    )

@dashboard_bp.route('/')
@login_required
def index():
    """
    توجيه تلقائي من المسار الجذري للموديول إلى لوحة التحكم.
    """
    return redirect(url_for('suppliers_dashboard.dashboard'))
