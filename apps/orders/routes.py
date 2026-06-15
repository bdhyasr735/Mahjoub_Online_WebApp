# 📂 apps/orders/routes.py
from flask import Blueprint, render_template, request, jsonify
from apps.models.order_db import Order
from apps.extensions import db
import logging

# إعداد الـ Logger لتتبع الأخطاء في سجلات Render
logger = logging.getLogger(__name__)

orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/admin/orders', methods=['GET'])
def orders_dashboard():
    try:
        # الحصول على رقم الصفحة من الرابط
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        # جلب الطلبات مع الترقيم
        # استخدام join(Order.supplier) يضمن جلب بيانات المورد مع الطلب في استعلام واحد (تحسين الأداء)
        pagination = Order.query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        orders = pagination.items
        
        return render_template('admin/orders_dashboard.html', 
                               orders=orders, 
                               pagination=pagination)
    
    except Exception as e:
        logger.error(f"Error in orders_dashboard: {str(e)}")
        # إرجاع رسالة خطأ واضحة أو صفحة 500 مخصصة
        return "حدث خطأ أثناء تحميل الطلبات، يرجى التأكد من أن قاعدة البيانات تحتوي على الجداول المطلوبة.", 500

@orders_bp.route('/admin/orders/update-status', methods=['POST'])
def update_order_status():
    """دالة لتحديث حالة الطلب عبر AJAX"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'بيانات غير صالحة'}), 400
            
        order_id = data.get('orderId')
        status_type = data.get('type')
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
        return jsonify({'success': False, 'message': 'فشل التحديث'}), 500
