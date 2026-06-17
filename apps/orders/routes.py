# coding: utf-8
# 📂 apps/admin_dashboard/routes.py - لوحة التحكم المركزية

from flask import Blueprint, render_template
from flask_login import login_required
from apps.models.orders_db import ProcessedOrder
from decimal import Decimal

admin_dashboard = Blueprint('admin_dashboard', __name__, template_folder='templates')

@admin_dashboard.route('/', methods=['GET'])
@login_required
def index():
    # 1. جلب كافة الطلبات
    all_orders = ProcessedOrder.query.all()
    
    # 2. حساب الإحصائيات مع فك التشفير التلقائي لكل طلب
    total_sales = sum([order.total_price for order in all_orders])
    total_count = len(all_orders)
    completed_count = len([o for o in all_orders if o.status == 'completed' or o.status == 'settled'])
    cancelled_count = len([o for o in all_orders if o.status == 'cancelled'])

    # 3. تمرير البيانات للوحة التحكم
    stats = {
        'total_sales': total_sales,
        'total_count': total_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count
    }

    return render_template('admin/dashboard.html', stats=stats)
