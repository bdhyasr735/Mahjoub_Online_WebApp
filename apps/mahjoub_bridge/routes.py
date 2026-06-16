# 📂 apps/mahjoub_bridge/routes.py
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
import logging

# استيراد الدوال المباشرة من الـ Engine
from apps.utils.products_engine import get_products_by_supplier, sync_products_to_db

logger = logging.getLogger(__name__)

# تعريف الـ Blueprint بالاسم المعتمد في المصنع
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
        # استدعاء الدالة المباشرة التي قمنا بتجهيزها في الـ Engine
        count = sync_products_to_db()
        return jsonify({'success': True, 'message': f'تمت مزامنة {count} منتج بنجاح.'})
    except Exception as e:
        logger.error(f"Error syncing products: {str(e)}")
        return jsonify({'success': False, 'message': 'فشل مزامنة المنتجات'}), 500

@products_bp.route('/list', methods=['GET'])
@login_required
def list_products():
    """عرض قائمة المنتجات"""
    # استقبال الـ tag للبحث (مثلاً: bridge/list?tag=my_supplier)
    search_tag = request.args.get('tag', 'all') 
    
    # استخدام الدالة المباشرة لجلب المنتجات المترجمة
    products = get_products_by_supplier(search_tag)
    
    return render_template('products/list.html', products=products)
