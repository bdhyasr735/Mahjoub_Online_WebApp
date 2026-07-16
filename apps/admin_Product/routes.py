# coding: utf-8
# 📂 apps/admin_Product/routes.py

import os
import requests  # استيراد مكتبة الـ requests
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required
from sqlalchemy.orm import lazyload
from datetime import datetime
from apps.models.product_db import Product
from apps.extensions import db, csrf
import logging

# تعريف البلوبرنت
admin_product_bp = Blueprint(
    'admin_product_bp', 
    __name__, 
    template_folder='templates'
)

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = Product.query.options(lazyload(Product.supplier))\
        .order_by(Product.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template(
        'admin/admin_Product.html', 
        products=pagination.items,
        pagination=pagination
    )

# --- المسار الجديد (الوكيل) لحل مشكلة CORS ---
@admin_product_bp.route('/proxy-sync', methods=['POST'])
@login_required
def proxy_sync():
    """مسار وكيل لجلب البيانات من قمرة لتجاوز مشاكل CORS"""
    query = "query { findAllProducts(page: 1, limit: 100) { items { _id title price sku } } }"
    headers = {
        "Authorization": f"Bearer {os.environ.get('QUMRA_API_KEY')}",
        "Content-Type": "application/json"
    }
    try:
        # السيرفر يتصل بـ قمرة بدلاً من المتصفح
        response = requests.post("https://api.qomrah.com/graphql", json={'query': query}, headers=headers, timeout=30)
        return jsonify(response.json())
    except Exception as e:
        logging.error(f"خطأ في البروكسي: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    try:
        data = request.json
        products_data = data.get('products', [])
        if not products_data:
            return jsonify({"status": "error", "message": "لا توجد بيانات للمزامنة"})

        count = 0
        for item in products_data:
            product = Product.query.filter_by(qid=str(item.get('_id'))).first()
            if not product:
                new_product = Product(
                    qid=str(item.get('_id')),
                    title=item.get('title', 'منتج غير معرف'),
                    supplier_id=1,
                    sku=item.get('sku', 'N/A'),
                    cost_price=float(item.get('price', 0))
                )
                db.session.add(new_product)
                count += 1
            else:
                product.title = item.get('title', product.title)
                product.cost_price = float(item.get('price', product.cost_price))
        
        db.session.commit()
        return jsonify({"status": "success", "message": f"تم حفظ {count} منتج جديد."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
