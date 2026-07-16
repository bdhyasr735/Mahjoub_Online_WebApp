# coding: utf-8
# 📂 apps/admin_Product/routes.py

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required
from sqlalchemy.orm import lazyload
from apps.models.product_db import Product
from apps.extensions import db, csrf
from apps.services.graphql_client import QomrahGraphQLClient
import logging

# تم تعديل الاسم إلى admin_product_bp ليتوافق مع المعايير
admin_product_bp = Blueprint(
    'admin_product_bp', 
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
    """إعادة توجيه آمنة باستخدام اسم البلوبرينت المحدث"""
    return redirect(url_for('admin_product_bp.manage_products'))

@admin_product_bp.route('/sync', methods=['POST'])
@login_required
@csrf.exempt 
def sync_products():
    """مسار المزامنة الفعلي مع قمرة"""
    try:
        logging.info("بدء عملية المزامنة...")
        
        products_data = QomrahGraphQLClient.fetch_products()
        
        if not products_data:
            return jsonify({"status": "error", "message": "لم يتم العثور على منتجات في قمرة"})

        for item in products_data:
            product = Product.query.filter_by(qid=str(item.get('_id'))).first()
            
            if not product:
                new_product = Product(
                    qid=str(item.get('_id')),
                    title=item.get('title', 'منتج غير معرف'),
                    supplier_id=1,
                    sku=item.get('sku', 'N/A')
                )
                new_product.cost_price = item.get('price', 0) 
                db.session.add(new_product)
            else:
                product.title = item.get('title', product.title)
                product.cost_price = item.get('price', product.cost_price)
        
        db.session.commit()
        logging.info(f"تمت مزامنة {len(products_data)} منتج بنجاح.")
        return jsonify({"status": "success", "message": f"تمت مزامنة {len(products_data)} منتج بنجاح!"})
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"خطأ أثناء المزامنة: {str(e)}")
        return jsonify({"status": "error", "message": "حدث خطأ داخلي أثناء المزامنة"}), 500
