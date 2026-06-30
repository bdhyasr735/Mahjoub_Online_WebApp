# coding: utf-8
# 📂 apps/admin_platform_treasury/routes.py

from flask import Blueprint, render_template, request
from flask_login import login_required
from apps.extensions import db
from .utils import get_treasury_stats, get_filtered_transactions

# تعريف الـ Blueprint
treasury_bp = Blueprint('treasury', __name__, template_folder='templates')

@treasury_bp.route('/dashboard', methods=['GET'])
@login_required
def treasury_dashboard():
    """
    عرض لوحة تحكم الخزينة (الأستاذ العام) مع فلترة دقيقة زمنياً.
    """
    # 1. استقبال المدخلات (الفلاتر) من الرابط
    currency = request.args.get('currency', 'all')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    
    # 2. استدعاء الإحصائيات العامة (الأرصدة)
    stats = get_treasury_stats()
    
    # 3. استدعاء الحركات المفلترة (باستخدام المرجع الزمني الموحد في الـ utils)
    # نمرر التاريخ والوقت لضمان دقة التقارير
    query = get_filtered_transactions(currency=currency, start_date=start_date, end_date=end_date)
    
    # 4. نظام التقسيم (Pagination) - عرض 15 حركة لكل صفحة
    pagination = query.paginate(page=page, per_page=15, error_out=False)
    
    return render_template(
        'admin_platform_treasury.html', 
        stats=stats, 
        transactions=pagination.items, 
        pagination=pagination,
        current_currency=currency,
        start_date=start_date,
        end_date=end_date
    )
