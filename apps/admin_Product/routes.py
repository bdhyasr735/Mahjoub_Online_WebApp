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
    # الاستعلام المحدث ليشمل كافة الحقول المطلوبة للبطاقات
    query = """
    query Data($input: GetAllProductsInput) {
      findAllProducts(input: $input) {
        data {
          qid
          title
          quantity
          pricing { costPrice }
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
    return jsonify({"status": "success", "data": data})

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    try:
        products_data = request.json.get('data', {}).get('findAllProducts', {}).get('data', [])
        
        for item in products_data:
            qid = str(item.get('qid'))
            product = Product.query.filter_by(qid=qid).first() or Product(qid=qid)
            
            # تحديث البيانات الأساسية
            product.title = item.get('title')
            product.quantity = item.get('quantity', 0)
            product.sku = item.get('identification', {}).get('sku')
            product.cost_price = item.get('pricing', {}).get('costPrice', 0.0)
            
            # تحديث البيانات المضافة (الصور والوزن)
            images = item.get('images', [])
            product.image_url = images[0].get('fileUrl') if images else None
            
            weight_info = item.get('weight', {})
            product.weight_val = weight_info.get('weight')
            product.weight_unit = weight_info.get('unit')
            
            db.session.add(product)
            
        db.session.commit()
        return jsonify({"status": "success", "message": "تمت مزامنة المنتجات وتحديث البيانات التفصيلية بنجاح"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
