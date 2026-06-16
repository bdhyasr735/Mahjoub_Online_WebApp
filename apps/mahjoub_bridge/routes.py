# 📂 apps/mahjoub_bridge/routes.py
from flask import Blueprint, render_template, request
from flask_login import login_required

# استدعاء دالة الجلب الحي فقط وحذف الدالة القديمة تماماً
from apps.utils.products_engine import get_products_by_supplier

products_bp = Blueprint('mahjoub_bridge', __name__, template_folder='templates')

@products_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('admin/bridge_dashboard.html')

@products_bp.route('/list', methods=['GET'])
@login_required
def list_products():
    search_tag = request.args.get('tag', 'all') 
    products = get_products_by_supplier(search_tag)
    return render_template('products/list.html', products=products)
