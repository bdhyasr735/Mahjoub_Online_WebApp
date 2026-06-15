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
    """عرض لوحة التحكم للطلبات"""
    try:
        page = request.args.get('page', 1, type=int)
        pagination = Order.query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=10, error_out=False
        )
        return render_template(
            'admin/orders_dashboard.html', 
            orders=pagination.items, 
            pagination=pagination
        )
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        return "حدث خطأ أثناء تحميل الطلبات", 500

@orders_bp.route('/admin/orders/sync', methods=['POST'])
@login_required
def sync_orders():
    """المسار المسؤول عن المزامنة باستخدام المحرك الموحد"""
    print("DEBUG: تم استدعاء مسار المزامنة عبر QumraBridgeEngine")
    try:
        engine = QumraBridgeEngine()
        # جلب الطلبات من قمرة باستخدام المحرك الموحد
        orders = engine.fetch_latest_orders()
        
        if not orders:
            return jsonify({'success': False, 'message': 'لم يتم العثور على طلبات أو خطأ في الصلاحيات (تأكد من orders:read).'})

        count = 0
        for item in orders:
            order_id = str(item.get('id'))
            if not order_id: continue
            
            # البحث عن الطلب أو إنشاؤه
            order = Order.query.filter_by(order_id_qumra=order_id).first() or Order(order_id_qumra=order_id)
            
            # تعبئة الحقول
            order.total = float(item.get('total', 0))
            order.status = item.get('status', 'pending')
            order.customer_name = item.get('customer', 'غير معروف')
            
            db.session.add(order)
            count += 1
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'تمت المزامنة بنجاح، عدد الطلبات المضافة/المحدثة: {count}'})
        
    except Exception as e:
        print(f"DEBUG: خطأ كارثي في المزامنة: {str(e)}")
        return jsonify({'success': False, 'message': f'فشل المزامنة: {str(e)}'}), 500

@orders_bp.route('/admin/orders/update-status', methods=['POST'])
@login_required
def update_order_status():
    """تحديث حالة الطلب محلياً"""
    try:
        data = request.json
        order = Order.query.get(data.get('orderId'))
        if not order:
            return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404
            
        order.status = data.get('value')
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم التحديث'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating status: {str(e)}")
        return jsonify({'success': False, 'message': 'خطأ في التحديث'}), 500
