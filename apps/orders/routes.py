# 📂 apps/orders/routes.py
from flask import Blueprint, render_template, request, jsonify
from apps.models.order_db import Order
from apps.utils.orders_engine import OrdersEngine
from flask_login import login_required
import logging

logger = logging.getLogger(__name__)
orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/admin/orders', methods=['GET'])
@login_required
def orders_dashboard():
    """عرض لوحة تحكم الطلبات"""
    page = request.args.get('page', 1, type=int)
    pagination = Order.query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template(
        'admin/orders_dashboard.html', 
        orders=pagination.items, 
        pagination=pagination
    )

@orders_bp.route('/admin/orders/sync', methods=['POST'])
@login_required
def sync_orders():
    """مزامنة الطلبات من قمرة إلى قاعدة البيانات"""
    try:
        engine = OrdersEngine()
        # هنا يتم استدعاء المحرك المحدث الذي يتعامل مع البيانات تلقائياً
        count = engine.sync_orders_to_db()
        return jsonify({
            'success': True, 
            'message': f'تمت المزامنة، تم معالجة {count} طلب بنجاح.'
        })
    except Exception as e:
        error_msg = f"فشل المزامنة: {str(e)}"
        logger.error(error_msg)
        return jsonify({'success': False, 'message': error_msg}), 500

@orders_bp.route('/admin/orders/update-status', methods=['POST'], endpoint='update_order_status')
@login_required
def update_order_status():
    """تحديث حالة الطلب يدوياً"""
    try:
        data = request.json
        order_id = data.get('orderId')
        new_status = data.get('value')
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404
            
        order.status = new_status
        from apps.extensions import db
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم تحديث الحالة بنجاح'})
    except Exception as e:
        logger.error(f"خطأ في تحديث الحالة: {str(e)}")
        return jsonify({'success': False, 'message': 'خطأ في الخادم أثناء التحديث'}), 500
