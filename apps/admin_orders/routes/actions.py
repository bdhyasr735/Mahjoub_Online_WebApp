from flask import Blueprint, render_template

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/api/orders/<int:order_id>/status')
def get_status_card(order_id):
    # 1. جلب البيانات من قاعدة البيانات
    order = Order.query.get_or_404(order_id)
    # 2. إرجاع قالب البطاقة فقط (وليس الصفحة كاملة)
    return render_template('admin/order/_order_status_card.html', order=order)

# كرر نفس المنطق لباقي البطاقات...
