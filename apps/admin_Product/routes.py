# 📂 apps/admin_Product/routes.py

from flask import Blueprint, render_template, request, jsonify
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

# --- المسار الذي كان يسبب الانهيار ---
@admin_product_bp.route('/add', methods=['GET'])
@login_required
def add_product():
    """عرض صفحة إضافة منتج جديد"""
    # إذا لم تكن قد أنشأت ملف admin_add_product.html بعد، 
    # يمكنك توجيهها لـ manage_products مؤقتاً لتجنب الخطأ
    return render_template('admin/admin_add_product.html')

@admin_product_bp.route('/sync', methods=['POST'])
@login_required
def sync_products():
    """مسار خاص ببدء المزامنة"""
    return jsonify({"status": "success", "message": "بدء عملية المزامنة..."})
