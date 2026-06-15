# 📂 apps/orders/routes.py
from flask import Blueprint, render_template, request, jsonify
from apps.models.order_db import Order
from apps.extensions import db
from apps.utils.orders_engine import OrdersEngine
from flask_login import login_required
import logging

# إعداد الـ Logger لتتبع الأخطاء في سجلات Render
logger = logging.getLogger(__name__)

# تعريف الـ Blueprint
orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/admin/orders', methods=['GET'])
@login_required
def orders_dashboard():
    """عرض لوحة التحكم الخاصة بالطلبات مع الترقيم"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        # استعلام لجلب الطلبات مرتبة من الأحدث للأقدم
        pagination = Order.query.order_by(Order.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        orders = pagination.items
        
        return render_template(
            'admin/orders_dashboard.html', 
            orders=orders, 
            pagination=pagination
        )
    
    except Exception as e:
        logger.error(f"Error in orders_dashboard: {str(e)}")
        return "حدث خطأ أثناء تحميل الطلبات، يرجى التأكد من اتصال قاعدة البيانات.", 500

@orders_bp.route('/admin/orders/sync', methods=['POST'])
@login_required
def sync_orders():
    """مسار لمزامنة الطلبات من قمرة إلى قاعدة البيانات المحلية"""
    try:
        # إنشاء المحرك والبدء بالمزامنة
        engine = OrdersEngine()
        engine.sync_orders_to_db()
        
        return jsonify({
            'success': True, 
            'message': 'تمت مزامنة الطلبات بنجاح من منصة قمرة.'
        })
    except Exception as e:
        # تسجيل الخطأ في سجلات Render للتشخيص
        logger.error(f"Sync error: {str(e)}")
        return jsonify({
            'success': False, 
            'message': 'فشل الاتصال بمنصة قمرة: ' + str(e)
        }), 500

@orders_bp.route('/admin/orders/update-status', methods=['POST'])
@login_required
def update_order_status():
    """دالة لتحديث حالة الطلب عبر طلب AJAX"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'بيانات غير صالحة'}), 400
            
        order_id = data.get('orderId')
        status_type = data.get('type') # 'payment' أو 'shipping'
        new_value = data.get('value')
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404
            
        if status_type == 'payment':
            order.payment_status = new_value
        elif status_type == 'shipping':
            order.status = new_value
            
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم التحديث بنجاح'})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update status error: {str(e)}")
        return jsonify({'success': False, 'message': 'فشل تحديث الحالة في قاعدة البيانات'}), 500
