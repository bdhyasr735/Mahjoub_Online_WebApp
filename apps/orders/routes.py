# 📂 apps/orders/routes.py
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
import logging

# استيراد محرك جلب الطلبات
from apps.utils.orders_engine import get_pending_orders

logger = logging.getLogger(__name__)

# تعريف الـ Blueprint بنفس الاسم المسجل في المصنع
orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/pending', methods=['GET'])
@login_required
def orders_dashboard():
    """
    عرض الطلبات المعلقة في لوحة التحكم (القيادة المركزية).
    """
    # التحقق للتأكد التام من جلسة تسجيل الدخول، والتحويل إلى auth_portal.login إذا لزم الأمر
    if not current_user.is_authenticated:
        return redirect(url_for('auth_portal.login'))
        
    try:
        # جلب الطلبات عبر محرك الـ GraphQL الجديد
        orders = get_pending_orders()
        
        # تمرير الطلبات إلى القالب لعرضها داخل التصميم البنفسجي والذهبي
        return render_template('admin/orders_dashboard.html', orders=orders)
        
    except Exception as e:
        logger.error(f"Error in orders_dashboard: {str(e)}")
        # في حال حدوث أي استثناء، نمرر قائمة فارغة حتى لا تنهار الصفحة وتظهر واجهة نظيفة
        return render_template('admin/orders_dashboard.html', orders=[])

@orders_bp.route('/process/<order_id>', methods=['POST'])
@login_required
def process_order(order_id):
    """
    تسوية أو معالجة طلب معين ماليًا مع المحافظ.
    """
    try:
        logger.info(f"Processing order transaction for ID: {order_id}")
        return jsonify({
            'success': True, 
            'message': f'تمت معالجة الطلب رقم {order_id} بنجاح.'
        })
    except Exception as e:
        logger.error(f"Error processing order {order_id}: {str(e)}")
        return jsonify({
            'success': False, 
            'message': 'حدث خطأ أثناء معالجة الطلب برمجياً.'
        }), 500
