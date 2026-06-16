# coding: utf-8
# 📂 apps/mahjoub_bridge/routes.py - النسخة النهائية الموحدة

from flask import Blueprint, render_template, request
from flask_login import login_required
# استيراد محرك الجسر المعتمد والمستقر
from apps.utils.bridge_engine import get_products_by_supplier

products_bp = Blueprint('mahjoub_bridge', __name__, template_folder='templates')

@products_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('admin/bridge_dashboard.html')

@products_bp.route('/list', methods=['GET'])
@login_required
def list_products():
    # استلام الوسم المطلوب من شريك النجاح
    search_tag = request.args.get('tag', 'all') 
    
    # جلب البيانات مباشرة من المحرك الموحد
    try:
        products = get_products_by_supplier(search_tag)
    except Exception as e:
        print(f"⚠️ خطأ أثناء جلب المنتجات: {e}")
        products = []

    return render_template('products/list.html', products=products)
