# coding: utf-8
# 📂 apps/mahjoub_bridge/routes.py - النسخة المحصنة والمطهرة للجسر

from flask import Blueprint, render_template, request
from flask_login import login_required

products_bp = Blueprint('mahjoub_bridge', __name__, template_folder='templates')

@products_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('admin/bridge_dashboard.html')

@products_bp.route('/list', methods=['GET'])
@login_required
def list_products():
    search_tag = request.args.get('tag', 'all') 
    
    # 🛡️ استيراد محلي ديناميكي لحماية السيرفر من الـ ImportError أثناء الإقلاع
    try:
        from apps.utils.products_engine import get_products_by_supplier
        products = get_products_by_supplier(search_tag)
    except ImportError:
        # حماية للطوارئ: في حال لم يجد الدالة بالاسم القديم، يعود بقائمة فارغة ولا يفصل السيرفر
        products = []
        print("⚠️ تنبيه سيادي: لم يتم العثور على الدالة get_products_by_supplier في محرك المنتجات.")

    return render_template('products/list.html', products=products)
