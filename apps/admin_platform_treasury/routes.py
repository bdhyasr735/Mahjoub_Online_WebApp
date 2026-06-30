# coding: utf-8
# 📂 apps/admin_platform_treasury/routes.py

from flask import Blueprint, render_template, request
from flask_login import login_required
from apps.extensions import db
from .utils import get_treasury_stats, get_filtered_transactions

treasury_bp = Blueprint('treasury', __name__, template_folder='templates', url_prefix='/admin/treasury')

@treasury_bp.route('/dashboard', methods=['GET'])
@login_required
def treasury_dashboard():
    """
    لوحة تحكم الخزينة (الأستاذ العام):
    يتم الآن عرض البيانات بنظام المدين (Debit) والدائن (Credit).
    """
    # 1. التقاط المدخلات
    currency = request.args.get('currency', 'all')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    
    # 2. جلب الإحصائيات (تأكد أن get_treasury_stats في utils تقوم بجمع debit و credit)
    stats = get_treasury_stats(db)
    
    # 3. جلب الاستعلام المفلتر
    # query الآن سيعيد كائنات تحتوي على debit و credit بدلاً من amount فقط
    query = get_filtered_transactions(
        currency=currency, 
        start_date=start_date, 
        end_date=end_date
    )
    
    # 4. تنفيذ التقسيم
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    
    return render_template(
        'admin_platform_treasury.html', 
        stats=stats, 
        transactions=pagination.items, 
        pagination=pagination,
        current_currency=currency,
        start_date=start_date,
        end_date=end_date
    )
