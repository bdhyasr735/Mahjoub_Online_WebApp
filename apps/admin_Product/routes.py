# coding: utf-8
# 📂 apps/admin_Product/routes.py

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from apps.services.product_sync_service import ProductSyncService

# تعريف الـ Blueprint للمنتجات
admin_product_bp = Blueprint(
    'admin_product_bp',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# مفتاح أو توكن الاتصال بالخادم المركزي
GRAPHQL_TOKEN = os.environ.get('QUMRA_API_KEY', 'YOUR_ADMIN_API_TOKEN')

@admin_product_bp.route('/products', methods=['GET'])
def manage_products():
    """عرض قائمة المنتجات مع دعم الترقيم والبحث المباشر عبر الـ API في جميع الصفحات"""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('title', '', type=str)
    
    client = ProductSyncService(token=GRAPHQL_TOKEN)
    
    # تمرير قيمة الـ search_query إلى الـ Service لتنفيذ البحث مباشرة في الخادم
    response_data = client.fetch_products(page=page, limit=20, title=search_query)
    
    products = response_data.get("data", [])
    pagination = response_data.get("pagination", {"currentPage": page, "totalPages": 1, "limit": 20})

    return render_template(
        'admin/admin_Product.html',
        products=products,
        search_title=search_query,
        pagination=pagination
    )

@admin_product_bp.route('/sync-products', methods=['POST'])
def sync_products():
    """مسار تنفيذ المزامنة عند النقر على الزر في نافذة الـ Modal"""
    try:
        client = ProductSyncService(token=GRAPHQL_TOKEN)
        
        raw_data = client.fetch_products(page=1, limit=50)
        
        if not raw_data or "data" not in raw_data:
            flash("تعذر جلب المنتجات من الخادم الخارجي أثناء المزامنة.", "danger")
            return redirect(url_for('admin_product_bp.manage_products'))

        count = len(raw_data.get("data", []))
        flash(f"تمت مزامنة البيانات بنجاح وجلب {count} منتجاً.", "success")
        
    except Exception as e:
        flash(f"حدث خطأ أثناء الاتصال بالمزامنة: {str(e)}", "danger")

    return redirect(url_for('admin_product_bp.manage_products'))

@admin_product_bp.route('/products/add', methods=['GET', 'POST'])
def add_product():
    """مسار إضافة منتج جديد"""
    return render_template('admin/add_product.html')

@admin_product_bp.route('/products/edit/<path:qid>', methods=['GET', 'POST'])
def edit_product(qid):
    """مسار تعديل المنتج باستخدام الـ qid الخاص به مع دعم المسارات الطويلة والرموز الخاصة"""
    print(f"DEBUG: Fetching product edit page for QID -> {qid}")
    
    client = ProductSyncService(token=GRAPHQL_TOKEN)
    product = client.fetch_product_by_qid(qid)
    
    print(f"DEBUG: Product fetch result -> {product}")
    
    if not product:
        flash("المنتج المطلوب غير موجود أو فشل جلب بياناته.", "danger")
        return redirect(url_for('admin_product_bp.manage_products'))
        
    return render_template('admin/admin_edit_product.html', product=product)
