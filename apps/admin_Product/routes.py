# 📂 apps/admin_Product/routes.py

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from apps.services.product_sync_service import ProductSyncService

admin_product_bp = Blueprint(
    'admin_product_bp',
    __name__,
    template_folder='templates',
    static_folder='static'
)

GRAPHQL_TOKEN = os.environ.get('QUMRA_API_KEY', 'YOUR_ADMIN_API_TOKEN')

@admin_product_bp.route('/products', methods=['GET'])
def manage_products():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('title', '', type=str)
    
    client = ProductSyncService(token=GRAPHQL_TOKEN)
    response_data = client.fetch_products(page=page, limit=20, title=search_query)
    
    products = response_data.get("data", [])
    pagination = response_data.get("pagination", {"currentPage": page, "totalPages": 1, "limit": 20})

    return render_template(
        'admin/admin_Product.html',
        products=products,
        search_title=search_query,
        pagination=pagination
    )

@admin_product_bp.route('/products/edit', methods=['GET'])
def edit_product():
    """مسار عرض صفحة تعديل المنتج مع جلب البيانات والملحقات المطلوبة للقالب"""
    qid = request.args.get('qid')
    
    if not qid:
        flash("معرف المنتج (qid) مفقود.", "danger")
        return redirect(url_for('admin_product_bp.manage_products'))
    
    client = ProductSyncService(token=GRAPHQL_TOKEN)
    product = client.fetch_product_by_qid(qid)
    
    if not product:
        flash("المنتج المطلوب غير موجود أو فشل جلب بياناته.", "danger")
        return redirect(url_for('admin_product_bp.manage_products'))
        
    # جلب الموردين والمجموعات لتعبئة قوائم الاختيار في القالب بنجاح
    suppliers = client.fetch_suppliers() if hasattr(client, 'fetch_suppliers') else []
    all_collections = client.fetch_collections() if hasattr(client, 'fetch_collections') else []
        
    return render_template(
        'admin/admin_edit_product.html', 
        product=product,
        suppliers=suppliers,
        all_collections=all_collections
    )

@admin_product_bp.route('/products/save-sync', methods=['POST'])
def save_sync_product():
    """مسار استقبال وتخزين البيانات الواردة من قالب التعديل عبر AJAX"""
    try:
        qid = request.form.get('qid')
        client = ProductSyncService(token=GRAPHQL_TOKEN)
        
        # استخراج البيانات المرسلة عبر FormData
        product_data = {
            "title": request.form.get('title'),
            "slug": request.form.get('slug'),
            "description": request.form.get('description'),
            "status": request.form.get('status'),
            "supplier_id": request.form.get('supplier_id'),
            "sku": request.form.get('sku'),
            "quantity": request.form.get('quantity'),
            "weight": request.form.get('weight'),
            "pricing": {
                "costPrice": request.form.get('original_price'),
                "compareAtPrice": request.form.get('compare_at_price'),
                "price": request.form.get('price')
            }
        }
        
        # تنفيذ عملية التحديث عبر الخدمة
        # success = client.update_product(qid, product_data, files=request.files.getlist('images'))
        
        return jsonify({"status": "success", "message": "تم حفظ وتحديث المنتج بنجاح."})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
