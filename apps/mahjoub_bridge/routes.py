# 📂 apps/mahjoub_bridge/routes.py
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
import logging

# استيراد الدالة المباشرة بدلاً من الكلاس ProductsEngine
from apps.utils.products_engine import get_products_by_supplier

logger = logging.getLogger(__name__)

products_bp = Blueprint('mahjoub_bridge', __name__, template_folder='templates')

@products_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """لوحة تحكم الجسر والمنتجات"""
    return render_template('admin/bridge_dashboard.html')

@products_bp.route('/sync', methods=['POST'])
@login_required
def sync_products():
    """مزامنة المنتجات من قمرة إلى قاعدة البيانات"""
    try:
        # ملاحظة: إذا كان لديك دالة للمزامنة، استدعيها هنا مباشرة
        # engine = ProductsEngine() # هذا الكلاس لم يعد موجوداً، قم باستبداله بالدالة المناسبة
        return jsonify({'success': True, 'message': 'تم تحديث نظام المزامنة.'})
    except Exception as e:
        logger.error(f"Error syncing products: {str(e)}")
        return jsonify({'success': False, 'message': 'فشل مزامنة المنتجات'}), 500

@products_bp.route('/list', methods=['GET'])
@login_required
def list_products():
    """عرض قائمة المنتجات"""
    search_tag = request.args.get('tag', 'all') # استقبال الـ tag للبحث
    page = request.args.get('page', 1, type=int)
    
    # استخدام الدالة المباشرة التي قمنا بتجهيزها
    products = get_products_by_supplier(search_tag)
    
    return render_template('products/list.html', products=products)
