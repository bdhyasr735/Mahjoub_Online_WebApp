# 📂 apps/orders/routes.py
from flask import Blueprint, render_template, request, jsonify
from apps.models.order_db import Order
from apps.extensions import db
from apps.utils.bridge_engine import QumraBridgeEngine
from flask_login import login_required
import logging

logger = logging.getLogger(__name__)
orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/admin/orders', methods=['GET'])
@login_required
def orders_dashboard():
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
    """المسار المسؤول عن مزامنة الطلبات من قمرة"""
    try:
        engine = QumraBridgeEngine()
        orders = engine.fetch_latest_orders()
        
        if not orders:
            return jsonify({'success': False, 'message': 'لم يتم العثور على طلبات جديدة.'})

        count = 0
        for item in orders:
            # استخدام المعرف الفريد _id القادم من قمرة
            order_id = str(item.get('_id', ''))
            if not order_id: continue
            
            order = Order.query.filter_by(order_id_qumra=order_id).first() or Order(order_id_qumra=order_id)
            
            # تحديث البيانات بناءً على هيكلية قمرة (totalPrice, status, account)
            order.total = float(item.get('totalPrice', 0))
            
            # معالجة الحالة (status)
            status_obj = item.get('status')
            order.status = status_obj.get('name', 'pending') if isinstance(status_obj, dict) else 'pending'
            
            # معالجة العميل (account)
            account_obj = item.get('account')
            order.customer_name = account_obj.get('name', 'غير معروف') if isinstance(account_obj, dict) else 'غير معروف'
            
            db.session.add(order)
            count += 1
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'تمت المزامنة بنجاح، تم تحديث {count} طلب.'})
        
    except Exception as e:
        logger.error(f"Sync error: {str(e)}")
        return jsonify({'success': False, 'message': f'خطأ أثناء المزامنة: {str(e)}'}), 500

@orders_bp.route('/admin/orders/update-status', methods=['POST'])
@login_required
def update_order_status():
    try:
        data = request.json
        order = Order.query.get(data.get('orderId'))
        if not order:
            return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404
            
        order.status = data.get('value')
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'خطأ في التحديث'}), 500
