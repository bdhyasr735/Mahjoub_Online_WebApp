# coding: utf-8
# 📂 apps/admin_Product/routes.py

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from apps.models.product_db import Product
from apps.extensions import db
from apps.services.graphql_client import QomrahGraphQLClient

admin_product_bp = Blueprint('admin_product_bp', __name__, template_folder='templates')

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.order_by(Product.created_at.desc()).paginate(page=page, per_page=12, error_out=False)
    return render_template('admin/admin_Product.html', products=pagination.items, pagination=pagination)

@admin_product_bp.route('/proxy-sync', methods=['POST'])
@login_required
def proxy_sync():
    query = """
    query Data($input: GetAllProductsInput) {
      findAllProducts(input: $input) {
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
    if not data:
        return jsonify({"status": "error", "message": "فشل الاتصال بخدمة المزامنة"}), 500
    
    # نرسل الـ data مباشرة كما تعودنا
    return jsonify({"status": "success", "data": data})

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    try:
        # هنا الـ payload القادم من الـ fetch في الفرونت إيند يجب أن يحتوي على المفتاح 'data'
        payload = request.json
        products_data = payload.get('data', {}).get('findAllProducts', {}).get('data', [])
        
        if not products_data:
            return jsonify({"status": "error", "message": "لا توجد بيانات للمزامنة"}), 400
        
        for item in products_data:
            qid = str(item.get('qid'))
            if not qid: continue
            
            product = Product.query.filter_by(qid=qid).first()
            if not product:
                product = Product(qid=qid, title=item.get('title') or "بدون عنوان")
            
            product.title = item.get('title') or product.title
            product.quantity = item.get('quantity', 0)
            product.sku = item.get('identification', {}).get('sku')
            product.cost_price = item.get('pricing', {}).get('price') or 0.0
            
            images = item.get('images', [])
            product.image_url = images[0].get('fileUrl') if images and isinstance(images, list) else None
            
            weight_info = item.get('weight', {}) or {}
            product.weight_val = weight_info.get('weight')
            product.weight_unit = weight_info.get('unit')
            
            db.session.add(product)
            
        db.session.commit()
        return jsonify({"status": "success", "message": f"تمت مزامنة {len(products_data)} منتج بنجاح"})
        
    except Exception as e:
        db.session.rollback()
        print(f"DEBUG SYNC ERROR: {str(e)}") 
        return jsonify({"status": "error", "message": str(e)}), 500
