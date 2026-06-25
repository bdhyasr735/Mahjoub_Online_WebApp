# coding: utf-8
# 📂 apps/suppliers_dashboard/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from apps.models.orders_db import Order # استيراد الموديل للتحقق منه

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
    نقطة الدخول للمسار الجذري (/suppliers/).
    إعادة توجيه ذكية للمستخدم المعتمد.
    """
    # التحقق من أن المستخدم لديه محفظة (يعني أنه مورد مسجل ومفعل)
    if hasattr(current_user, 'wallet') and current_user.wallet:
        return redirect(url_for('suppliers_dashboard.dashboard'))
    
    return "عذراً، هذا الحساب غير مخصص للوصول إلى لوحة الموردين."

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """
    لوحة تحكم المورد الرئيسية.
    تعرض الأرصدة المالية وإحصائيات الطلبات.
    """
    # 1. التحقق من صلاحية الوصول للمحفظة
    if not hasattr(current_user, 'wallet') or current_user.wallet is None:
        flash("يجب ربط محفظة بحسابك للوصول للوحة التحكم.", "warning")
        return redirect(url_for('suppliers_dashboard.index'))

    # 2. حساب الطلبات قيد التنفيذ باستخدام الاستعلام المباشر (أسرع من معالجة القائمة برمجياً)
    # ملاحظة: إذا كان current_user هو المورد، فلديه علاقة 'orders' مباشرة
    pending_orders_count = Order.query.filter_by(
        supplier_id=current_user.id, 
        status='pending'
    ).count()
    
    # 3. عرض البيانات
    return render_template(
        'suppliers/dashboard.html', 
        pending_orders_count=pending_orders_count
    )

@dashboard_bp.route('/settings')
@login_required
def settings():
    """
    صفحة إعدادات المتجر وبيانات الحساب.
    """
    return render_template('suppliers/settings.html')
