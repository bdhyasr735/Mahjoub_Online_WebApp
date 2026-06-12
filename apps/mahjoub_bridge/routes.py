# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from apps import db
from apps.models.bridge_db import Product, ProductVariant, encrypt, decrypt
from apps.utils.bridge_engine import QumraBridgeEngine

bridge_bp = Blueprint('mahjoub_bridge', __name__, template_folder='templates')

@bridge_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """عرض لوحة التحكم مع نظام ترقيم الصفحات وتأمين فك التشفير"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 16
        pagination = Product.query.order_by(Product.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
        products = pagination.items
        
        # دالة آمنة لفحص فك التشفير
        def safe_decrypt(value):
            try:
                return decrypt(value)
            except:
                return "0.00" # في حال كان المنتج تالفاً أو غير مشفر بشكل صحيح

        return render_template('admin/bridge_dashboard.html', 
                               products=products, 
                               pagination=pagination, 
                               page=page, 
                               decrypt=safe_decrypt) 
                               
    except Exception as e:
        # تسجيل الخطأ في السجلات (Logs)
        print(f"Error in bridge dashboard: {str(e)}")
        flash(f"حدث خطأ أثناء تحميل البيانات: {str(e)}", "danger")
        return redirect(url_for('admin_dashboard.dashboard'))

# ... (بقية الدوال تبقى كما هي)
