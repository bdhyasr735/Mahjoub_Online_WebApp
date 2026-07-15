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
    
    # إعدادات التقليب: 10 منتجات في كل صفحة
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # جلب المنتجات (يمكنك إضافة منطق الفلترة هنا لاحقاً)
    pagination = Product.query.order_by(Product.created_at.desc()).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    products = pagination.items
    
    return render_template(
        'admin/admin_Product.html', 
        products=products,
        pagination=pagination
    )

@admin_product_bp.route('/sync', methods=['POST'])
@login_required
def sync_products():
    """مسار خاص ببدء المزامنة (سيتم ربطه بـ registry)"""
    # هنا سيتم استدعاء وظيفة المزامنة لاحقاً
    return jsonify({"status": "success", "message": "بدء عملية المزامنة..."})
