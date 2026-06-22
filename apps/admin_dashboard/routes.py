# 📂 apps/vendor_dashboard/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from apps.models.supplier_profile_db import SupplierProfile
from apps.models.supplier_db import Supplier # تأكد من استيراد الموديل

dashboard_bp = Blueprint('vendor_dashboard', __name__, template_folder='templates')

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """
    لوحة تحكم المورد: جلب البيانات بناءً على هوية المورد الحالية
    """
    
    # 1. البحث عن البروفايل يدوياً بناءً على ID المورد الحالي
    # بما أننا لا نعدل الجداول، نبحث في البروفايلات عن صاحب هذا الـ ID
    profile = SupplierProfile.query.filter_by(user_id=current_user.id).first()
    
    # 2. إذا لم يوجد بروفايل، يجب إكمال الإعداد
    if not profile:
        return redirect(url_for('vendors.setup_profile'))

    try:
        # 3. جلب الإحصائيات (نستخدم current_user لأنه كائن Supplier الفعلي)
        supplier_stats = {
            'total_sales': getattr(current_user, 'get_total_sales', lambda: "0.00")(),
            'pending_orders': getattr(current_user, 'get_pending_orders_count', lambda: 0)()
        }
    except Exception as e:
        print(f"DEBUG: Data Error: {e}")
        supplier_stats = {'total_sales': "0.00", 'pending_orders': 0}

    return render_template(
        'vendor/dashboard.html', 
        profile=profile,
        supplier_stats=supplier_stats
    )
