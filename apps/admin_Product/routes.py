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

@admin_product_bp.route('/products', methods=['GET'])
def manage_products():
    """عرض قائمة المنتجات مع دعم الترقيم والبحث المستقر محلياً"""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('title', '', type=str)
    
    token = os.environ.get('QUMRA_API_KEY') or os.environ.get('GRAPHQL_ENDPOINT')
    client = ProductSyncService(token=token)
    
    # جلب المنتجات بالهيكل الأساسي الصحيح لتفادي أخطاء الـ API
    response_data = client.fetch_products(page=page, limit=20)
    
    products = response_data.get("data", [])
    pagination = response_data.get("pagination", {"currentPage": page, "totalPages": 1, "limit": 20})
    
    # تصفية محلية آمنة للبحث بالاسم
    if search_query:
        products = [p for p in products if search_query.lower() in p.get('title', '').lower()]

    return render_template(
        'admin/admin_Product.html',
        products=products,
        search=search_query,
        pagination=pagination
    )

@admin_product_bp.route('/sync-products', methods=['POST'])
def sync_products():
    """مسار تنفيذ المزامنة عند النقر على الزر في نافذة الـ Modal"""
    try:
        token = os.environ.get('QUMRA_API_KEY') or os.environ.get('GRAPHQL_ENDPOINT')
        client = ProductSyncService(token=token)
        
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

@admin_product_bp.route('/products/edit/<qid>', methods=['GET', 'POST'])
def edit_product(qid):
    """مسار تعديل المنتج باستخدام الـ qid الخاص به"""
    token = os.environ.get('QUMRA_API_KEY') or os.environ.get('GRAPHQL_ENDPOINT')
    client = ProductSyncService(token=token)
    
    product = client.fetch_product_by_qid(qid)
    
    if not product:
        flash("المنتج المطلوب غير موجود.", "danger")
        return redirect(url_for('admin_product_bp.manage_products'))
        
    # تم التصحيح ليتطابق مع اسم القالب الموجود لديك admin_edit_product.html
    return render_template('admin/admin_edit_product.html', product=product)
