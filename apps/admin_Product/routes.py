# coding: utf-8
# 📂 apps/admin_Product/routes.py

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from apps.models.product_db import Product
from apps.extensions import db
from apps.services.graphql_client import QomrahGraphQLClient

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
    pagination = Product.query.order_by(Product.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template(
        'admin/admin_Product.html', 
        products=pagination.items,
        pagination=pagination
    )

@admin_product_bp.route('/proxy-sync', methods=['POST'])
@login_required
def proxy_sync():
    """الوكيل لجلب المنتجات باستخدام الحقول الصحيحة والمتداخلة"""
    
    # الاستعلام المحدث بناءً على Schema الـ API
    query = """
    query { 
        findAllProducts(input: {}) { 
            data { 
                qid 
                title 
                pricing { price } 
                identification { sku } 
            } 
        } 
    }
    """
    
    data = QomrahGraphQLClient.execute_query(query)
    
    if data is None or 'findAllProducts' not in data:
        return jsonify({
            "status": "error", 
            "message": "فشل جلب البيانات من المصدر."
        }), 500
        
    return jsonify({"status": "success", "data": data['findAllProducts']['data']})

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    """حفظ البيانات المجلوبة مع مراعاة الحقول المتداخلة"""
    try:
        data = request.json
        products_data = data.get('products', [])
        
        if not products_data:
            return jsonify({"status": "error", "message": "لا توجد منتجات للمزامنة"})

        count = 0
        for item in products_data:
            qid = str(item.get('qid')) # المعرف الفريد للمنتج
            product = Product.query.filter_by(qid=qid).first()
            
            # استخراج القيم من الحقول المتداخلة
            pricing = item.get('pricing', {}) or {}
            identification = item.get('identification', {}) or {}
            
            try:
                price = float(pricing.get('price', 0))
            except (ValueError, TypeError):
                price = 0.0

            if not product:
                # بفضل تعديل الموديل ليصبح supplier_id قابل للـ NULL، لن يحدث خطأ هنا
                new_product = Product(
                    qid=qid,
                    title=item.get('title', 'منتج غير معرف'),
                    sku=identification.get('sku', 'N/A'),
                    cost_price=price
                )
                db.session.add(new_product)
                count += 1
            else:
                product.title = item.get('title', product.title)
                product.cost_price = price
                product.sku = identification.get('sku', product.sku)
        
        db.session.commit()
        return jsonify({
            "status": "success", 
            "message": f"تمت المزامنة بنجاح: تمت معالجة {len(products_data)} منتج."
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"خطأ في الحفظ: {str(e)}"}), 500
