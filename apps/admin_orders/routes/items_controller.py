from flask import Blueprint, render_template
# استيراد نموذج الطلب الخاص بك
# from .models import Order

# تسمية الـ Blueprint بما يتوافق مع وحدات النظام
order_cards_bp = Blueprint('order_cards_bp', __name__)

# 1. بطاقة حالة الطلب
@order_cards_bp.route('/api/orders/<int:order_id>/status')
def get_status_card(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order/_order_status_card.html', order=order)

# 2. بطاقة معلومات العميل
@order_cards_bp.route('/api/orders/<int:order_id>/customer')
def get_customer_card(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order/_customer_info_card.html', order=order)

# 3. بطاقة الملخص المالي
@order_cards_bp.route('/api/orders/<int:order_id>/financials')
def get_financials_card(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order/_financial_summary_card.html', order=order)

# 4. بطاقة إحصائيات المورد
@order_cards_bp.route('/api/orders/<int:order_id>/supplier-stats')
def get_supplier_stats_card(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order/_supplier_stats_card.html', order=order)
