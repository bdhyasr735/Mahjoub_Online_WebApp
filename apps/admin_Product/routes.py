# 📂 apps/admin_Product/routes.py

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required
from apps.models.product_db import Product

# تعريف البلوبرينت
admin_product_bp = Blueprint(
    'admin_product', 
    __name__, 
    template_folder='templates'
)

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    """عرض قائمة المنتجات بنظام الصفحات (Pagination)"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    pagination = Product.query.order_by(Product.created_at.desc()).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return render_template(
        'admin/admin_Product.html', 
        products=pagination.items,
        pagination=pagination
    )

@admin_product_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """
    مسار آمن لإضافة منتج:
    في حال لم تكن صفحة admin_add_product.html جاهزة بعد، 
    سيعيد النظام توجيه المستخدم للقائمة بدلاً من الانهيار.
    """
    try:
        return render_template('admin/admin_add_product.html')
    except Exception:
        # في حال عدم وجود الملف، يتم تحويل الطلب للقائمة الرئيسية بأمان
        return redirect(url_for('admin_product.manage_products'))

@admin_product_bp.route('/sync', methods=['POST'])
@login_required
def sync_products():
    """مسار خاص ببدء المزامنة"""
    return jsonify({"status": "success", "message": "بدء عملية المزامنة..."})
