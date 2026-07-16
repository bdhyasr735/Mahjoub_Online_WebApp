# coding: utf-8
# 📂 apps/admin_Product/routes.py

import os
import requests
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from sqlalchemy.orm import lazyload
from apps.models.product_db import Product
from apps.extensions import db

# تعريف البلوبرنت الخاص بإدارة المنتجات
admin_product_bp = Blueprint(
    'admin_product_bp', 
    __name__, 
    template_folder='templates'
)

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    """عرض قائمة المنتجات مع نظام التصفح"""
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

@admin_product_bp.route('/proxy-sync', methods=['POST'])
@login_required
def proxy_sync():
    """الوكيل (Proxy) لجلب البيانات من قمرة بشكل آمن ومخفي عن المتصفح"""
    api_key = os.environ.get('QUMRA_API_KEY')
    
    if not api_key:
        return jsonify({"status": "error", "message": "API Key غير متاح في إعدادات السيرفر"}), 500

    query = "query { findAllProducts(page: 1, limit: 100) { items { _id title price sku } } }"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            "https://api.qomrah.com/graphql", 
            json={'query': query}, 
            headers=headers, 
            timeout=45
        )
        
        # التأكد من نجاح الاتصال بـ قمرة
        if response.status_code != 200:
            return jsonify({"status": "error", "message": f"خطأ من قمرة: {response.status_code}"}), response.status_code
            
        return jsonify(response.json())
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"فشل الاتصال بـ قمرة: {str(e)}"}), 500

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    """حفظ البيانات المجلوبة في قاعدة البيانات المحلية"""
    try:
        data = request.json
        products_data = data.get('products', [])
        
        if not products_data:
            return jsonify({"status": "error", "message": "لا توجد منتجات للمزامنة"})

        count = 0
        for item in products_data:
            # التأكد من تحويل القيم بشكل آمن
            qid = str(item.get('_id'))
            product = Product.query.filter_by(qid=qid).first()
            
            # محاولة تحويل السعر لـ float مع معالجة الأخطاء
            try:
                price = float(item.get('price', 0))
            except (ValueError, TypeError):
                price = 0.0

            if not product:
                # إنشاء منتج جديد
                new_product = Product(
                    qid=qid,
                    title=item.get('title', 'منتج غير معرف'),
                    supplier_id=1,
                    sku=item.get('sku', 'N/A'),
                    cost_price=price
                )
                db.session.add(new_product)
                count += 1
            else:
                # تحديث بيانات المنتج الموجود
                product.title = item.get('title', product.title)
                product.cost_price = price
        
        db.session.commit()
        return jsonify({
            "status": "success", 
            "message": f"تمت معالجة {len(products_data)} منتج، وتم إضافة {count} منتج جديد."
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"خطأ في حفظ البيانات: {str(e)}"}), 500
