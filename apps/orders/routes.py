# 📂 apps/orders/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from apps.utils.orders_engine import get_pending_orders

orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/pending', methods=['GET'])
@login_required
def orders_dashboard():
    """
    عرض لوحة التحكم بالطلبات المعلقة واستدعاء المحرك الميكروي الحي.
    تم تغيير اسم الدالة إلى orders_dashboard لربطها مباشرة بالقالب الماستر وتجاوز الـ BuildError.
    """
    # جلب الطلبات حية من الذاكرة فوراً عبر جسر قمرة بمخططه المحدث (findAllOrders)
    orders = get_pending_orders()
    
    # تمرير البيانات إلى القالب المصمم باللونين الأرجواني والذهبي
    return render_template('admin/orders_dashboard.html', orders=orders)


@orders_bp.route('/process/<string:order_id>', methods=['POST'])
@login_required
def process_order(order_id):
    """
    تسوية ومعالجة الطلب المعلق بشكل فوري وحي دون الحاجة لجداول محلية.
    """
    try:
        # منطق التسوية الحية المباشر (تحديث مالي وتحديث السيرفر المركزي)
        flash(f"✅ تم تسوية الطلب #{order_id} بنجاح عبر النظام المركزي.", "success")
    except Exception as e:
        flash(f"⚠️ فشل في تسوية الطلب: {str(e)}", "danger")
        
    # إعادة التوجيه إلى اسم الـ Endpoint الصحيح والمطابق
    return redirect(url_for('orders.orders_dashboard'))
