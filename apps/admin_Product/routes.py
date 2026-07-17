# coding: utf-8
# 📂 apps/admin_Product/routes.py

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from apps.models.product_db import Product
from apps.extensions import db
from apps.services.graphql_client import QomrahGraphQLClient
from sqlalchemy import or_

admin_product_bp = Blueprint('admin_product_bp', __name__, template_folder='templates')

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Product.query
    if search:
        query = query.filter(or_(Product.title.contains(search), Product.sku.contains(search)))
        
    # زيادة عدد العناصر في الصفحة الواحدة لـ 20
    pagination = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/admin_Product.html', 
                           products=pagination.items, 
                           pagination=pagination, 
                           search=search)

@admin_product_bp.route('/proxy-sync', methods=['POST'])
@login_required
def proxy_sync():
    # هنا التعديل الجوهري: إضافة limit كبير لجلب كافة المنتجات
    query = """
    query Data {
      findAllProducts(input: { limit: 5000 }) {
        data {
          qid
          title
          quantity
          pricing { price }
          images { fileUrl }
          weight { weight unit }
          identification { sku }
        }
      }
    }
    """
    data = QomrahGraphQLClient.execute_query(query)
    if not data or 'data' not in data:
        return jsonify({"status": "error", "message": "فشل الاتصال بخدمة المزامنة"}), 500
    
    return jsonify({"status": "success", "data": data})

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    try:
        payload = request.json
        products_data = payload.get('products', []) 
        
        if not products_data:
            return jsonify({"status": "error", "message": "لا توجد منتجات لحفظها"}), 400
        
        for item in products_data:
            qid = str(item.get('qid'))
            if not qid: continue
            
            product = Product.query.filter_by(qid=qid).first()
            if not product:
                product = Product(qid=qid)
                db.session.add(product)
            
            product.title = item.get('title') or "بدون عنوان"
            product.quantity = item.get('quantity', 0)
            product.sku = item.get('identification', {}).get('sku') if item.get('identification') else None
            product.cost_price = item.get('pricing', {}).get('price') or 0.0
            
            images = item.get('images', [])
            product.image_url = images[0].get('fileUrl') if isinstance(images, list) and images else None
            
            weight_info = item.get('weight', {}) or {}
            product.weight_val = weight_info.get('weight')
            product.weight_unit = weight_info.get('unit')
            
        db.session.commit()
        return jsonify({"status": "success", "message": f"تمت مزامنة {len(products_data)} منتج"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# ... (دالة edit_product تبقى كما هي)
