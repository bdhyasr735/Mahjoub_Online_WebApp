# 📂 apps/admin_Product/routes.py

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required
from sqlalchemy.orm import lazyload
from apps.models.product_db import Product
from apps.extensions import db
# استيراد الكلاس الموحد للاتصال بـ قمرة
from apps.services.graphql_client import QomrahGraphQLClient

# تعريف البلوبرينت
admin_product_bp = Blueprint(
    'admin_product', 
    __name__, 
    template_folder='templates'
)

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    """عرض قائمة المنتجات بنظام الصفحات"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    pagination = Product.query.options(lazyload(Product.supplier))\
        .order_by(Product.created_at.desc())\
        .paginate(
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
    """مسار آمن يعرض قائمة المنتجات"""
    return redirect(url_for('admin_product.manage_products'))

@admin_product_bp.route('/sync', methods=['POST'])
@login_required
def sync_products():
    """مسار المزامنة الفعلي الذي يتصل بـ قمرة عبر الكلاس QomrahGraphQLClient"""
    try:
        # 1. جلب المنتجات من قمرة باستخدام الكلاس
        # تأكد أن الكلاس QomrahGraphQLClient يحتوي على دالة fetch_products
        products_data = QomrahGraphQLClient.fetch_products()
        
        if not products_data:
            return jsonify({"status": "error", "message": "لم يتم العثور على منتجات في قمرة"})

        # 2. تحديث قاعدة البيانات
        for item in products_data:
            # البحث عن المنتج بـ qid (المعرف القادم من قمرة)
            product = Product.query.filter_by(qid=str(item.get('_id'))).first()
            
            if not product:
                # إنشاء منتج جديد
                new_product = Product(
                    qid=str(item.get('_id')),
                    title=item.get('title', 'منتج غير معرف'),
                    supplier_id=1, # المورد الافتراضي
                    sku=item.get('sku', 'N/A')
                )
                new_product.cost_price = item.get('price', 0) 
                db.session.add(new_product)
            else:
                # تحديث البيانات الموجودة
                product.title = item.get('title', product.title)
                product.cost_price = item.get('price', product.cost_price)
        
        db.session.commit()
        return jsonify({"status": "success", "message": f"تمت مزامنة {len(products_data)} منتج بنجاح!"})
        
    except Exception as e:
        db.session.rollback()
        # تسجيل الخطأ لسهولة التتبع
        import logging
        logging.error(f"Error during sync: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
