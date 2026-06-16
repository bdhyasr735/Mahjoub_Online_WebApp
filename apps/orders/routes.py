# 📂 apps/orders/routes.py
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
import logging

# استيراد محرك الطلبات
from apps.utils.orders_engine import get_pending_orders

logger = logging.getLogger(__name__)

# تعريف الـ Blueprint
orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/pending', methods=['GET'])
@login_required
def orders_dashboard():
    """
    عرض الطلبات المعلقة في لوحة التحكم (القيادة المركزية).
    """
    try:
        # جلب الطلبات من المحرك
        orders = get_pending_orders()
        
        # تمرير الطلبات إلى القالب
        return render_template('admin/orders_dashboard.html', orders=orders)
        
    except Exception as e:
        logger.error(f"Error in orders_dashboard: {str(e)}")
        # في حال حدوث خطأ، نرسل قائمة فارغة للقالب لمنع الانهيار
        return render_template('admin/orders_dashboard.html', orders=[])

@orders_bp.route('/process/<order_id>', methods=['POST'])
@login_required
def process_order(order_id):
    """
    تسوية أو معالجة طلب معين.
    """
    try:
        # هنا سيتم لاحقاً إضافة منطق الربط مع محفظة المورد
        logger.info(f"Processing order: {order_id}")
        return jsonify({
            'success': True, 
            'message': f'تمت معالجة الطلب رقم {order_id} بنجاح.'
        })
    except Exception as e:
        logger.error(f"Error processing order {order_id}: {str(e)}")
        return jsonify({
            'success': False, 
            'message': 'حدث خطأ أثناء معالجة الطلب.'
        }), 500
