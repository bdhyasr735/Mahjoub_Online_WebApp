# coding: utf-8
# 📂 apps/suppliers_dashboard/routes.py

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

# تعريف الـ Blueprint مع تحديد مسار القوالب لضمان العزل
dashboard_bp = Blueprint(
    'suppliers_dashboard', 
    __name__, 
    template_folder='templates'
)

@dashboard_bp.route('/')
@login_required
def index():
    """
    نقطة الدخول للمسار الجذري (/suppliers/).
    يتم إعادة التوجيه تلقائياً إلى لوحة التحكم إذا كان المستخدم مورداً مؤهلاً.
    """
    if hasattr(current_user, 'wallet') and current_user.wallet is not None:
        return redirect(url_for('suppliers_dashboard.dashboard'))
    
    return "عذراً، لا تمتلك صلاحية الوصول لهذه المنطقة."

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """
    لوحة تحكم المورد الرئيسية.
    تستعلم عن بيانات المحفظة والطلبات وتعرضها في قالب dashboard.html
    """
    # 1. التحقق من وجود المحفظة لتجنب أي خطأ برمجي
    if not hasattr(current_user, 'wallet') or current_user.wallet is None:
        return redirect(url_for('suppliers_dashboard.index'))

    # 2. جلب كائن المحفظة
    wallet = current_user.wallet
    
    # 3. حساب الطلبات قيد التنفيذ
    pending_orders_count = 0
    if hasattr(current_user, 'orders') and current_user.orders:
        pending_orders_count = len([o for o in current_user.orders if o.status == 'pending'])
    
    # 4. تمرير البيانات للقالب (داخل المجلد الفرعي 'suppliers')
    # لاحظ أننا نمرر wallet أيضاً ليستخدمه القالب في عرض الأرصدة
    return render_template(
        'suppliers/dashboard.html', 
        wallet=wallet,
        pending_orders_count=pending_orders_count
    )

@dashboard_bp.route('/settings')
@login_required
def settings():
    """
    صفحة إعدادات المتجر.
    تعرض بيانات المورد وتسمح بإدارة الحساب.
    """
    return render_template('suppliers/settings.html')
