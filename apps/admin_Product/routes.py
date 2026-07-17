# coding: utf-8
# 📂 apps/admin_Product/routes.py

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
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

# --- مسار صفحة التعديل مع ربط قمرة ---
@admin_product_bp.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        # 1. تحديث القيم في قاعدة البيانات المحلية
        product.title = request.form.get('title', product.title)
        product.quantity = request.form.get('quantity', product.quantity)
        product.cost_price = request.form.get('cost_price', product.cost_price)
        product.sku = request.form.get('sku', product.sku)
        product.weight_val = request.form.get('weight_val', product.weight_val)
        
        # 2. إرسال التعديلات إلى قمرة (Mutation)
        mutation = """
        mutation UpdateProduct($id: ID!, $input: UpdateProductInput!) {
            updateProduct(id: $id, input: $input) {
                success
                message
            }
        }
        """
        variables = {
            "id": product.qid,
            "input": {
                "title": product.title,
                "quantity": int(product.quantity),
                "price": float(product.cost_price),
                "sku": product.sku
            }
        }
        
        try:
            # افتراض أن execute_query هي الدالة المستخدمة في QomrahGraphQLClient
            response = QomrahGraphQLClient.execute_query(mutation, variables=variables)
            
            if response and response.get('data', {}).get('updateProduct', {}).get('success'):
                db.session.commit()
                flash('تم تحديث بيانات المنتج في المتجر (قمرة) ومحلياً بنجاح', 'success')
            else:
                flash('تم التحديث محلياً، ولكن فشل الربط مع منصة قمرة', 'warning')
        except Exception as e:
            flash(f'خطأ أثناء الاتصال بقمرة: {str(e)}', 'danger')
            
        return redirect(url_for('admin_product_bp.manage_products'))
        
    return render_template('admin/edit_product.html', product=product)

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
    
    return jsonify({"status": "success", "data": data})

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    try:
        payload = request.json
        products_data = payload.get('products', []) 
        
        if not products_data:
            return jsonify({"status": "error", "message": "لم يتم استقبال أي منتجات للحفظ"}), 400
        
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
        return jsonify({"status": "success", "message": f"تمت مزامنة {len(products_data)} منتج بنجاح"})
        
    except Exception as e:
        db.session.rollback()
        print(f"CRITICAL SYNC ERROR: {str(e)}") 
        return jsonify({"status": "error", "message": str(e)}), 500
