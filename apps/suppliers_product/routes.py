
# coding: utf-8
# 📂 apps/suppliers_product/routes.py

import os
import json
from flask import Blueprint, render_template, request, jsonify, abort, session
from flask_login import login_required, current_user
from apps.services.product_sync_service import ProductSyncService
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier
from apps.extensions import db

# تعريف الـ Blueprint
suppliers_product_bp = Blueprint(
    'suppliers_product_bp',
    __name__,
    template_folder='templates'
)

GRAPHQL_TOKEN = os.environ.get('QUMRA_API_KEY', 'YOUR_ADMIN_API_TOKEN')


# ============================================================
# 🟣 مسار عرض منتجات المورد
# ============================================================
@suppliers_product_bp.route('/products', methods=['GET'])
@login_required
def products():
    """عرض منتجات المورد المرتبطة به فقط."""
    
    # التحقق من أن المستخدم هو مورد
    user_type = session.get('user_type')
    if user_type not in ['supplier', 'staff']:
        abort(403)
    
    # تحديد supplier_id
    if user_type == 'staff':
        supplier_id = current_user.supplier_id
    else:
        supplier_id = current_user.id
    
    # جلب المورد
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        abort(404)
    
    # جلب جميع المنتجات المرتبطة بهذا المورد
    mappings = ProductSupplierMapping.query.filter_by(
        supplier_id=supplier_id,
        status='active'
    ).all()
    
    product_qids = [m.product_qid for m in mappings]
    
    # جلب بيانات المنتجات من Qumra
    sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
    products = []
    
    for qid in product_qids:
        product = sync_service.fetch_product_by_qid(qid)
        if product:
            products.append(product)
    
    # ✅ البحث (اختياري)
    search_query = request.args.get('search', '').strip()
    if search_query:
        products = [
            p for p in products 
            if search_query.lower() in p.get('title', '').lower() 
            or search_query.lower() in p.get('ident', {}).get('sku', '').lower()
        ]
    
    # ✅ تحديد طريقة العرض (بطاقات أو جدول)
    view = request.args.get('view', 'grid')
    
    # ✅ إذا كان طلب AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if view == 'list':
            return render_template(
                'suppliers/includes/_product_table.html',
                products=products
            )
        else:
            return render_template(
                'suppliers/includes/_product_cards.html',
                products=products
            )
    
    return render_template(
        'suppliers/suppliers_product.html',
        products=products,
        view=view
    )


# ============================================================
# 🟣 مسار عرض تفاصيل منتج معين
# ============================================================
@suppliers_product_bp.route('/product/<qid>', methods=['GET'])
@login_required
def view_product(qid):
    """عرض تفاصيل منتج معين للمورد."""
    
    # التحقق من أن المستخدم هو مورد
    user_type = session.get('user_type')
    if user_type not in ['supplier', 'staff']:
        abort(403)
    
    # تحديد supplier_id
    if user_type == 'staff':
        supplier_id = current_user.supplier_id
    else:
        supplier_id = current_user.id
    
    # التحقق من أن المنتج مرتبط بهذا المورد
    mapping = ProductSupplierMapping.query.filter_by(
        product_qid=qid,
        supplier_id=supplier_id,
        status='active'
    ).first()
    
    if not mapping:
        abort(404)
    
    # جلب بيانات المنتج من Qumra
    sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
    product = sync_service.fetch_product_by_qid(qid)
    
    if not product:
        abort(404)
    
    return render_template(
        'suppliers/product_detail.html',
        product=product,
        supplier=Supplier.query.get(supplier_id)
    )


# ============================================================
# 🟣 مسار مزامنة منتجات المورد (اختياري)
# ============================================================
@suppliers_product_bp.route('/sync', methods=['POST'])
@login_required
def sync_products():
    """مزامنة منتجات المورد مع Qumra."""
    
    # التحقق من أن المستخدم هو مورد
    user_type = session.get('user_type')
    if user_type not in ['supplier', 'staff']:
        return jsonify({"success": False, "message": "غير مصرح لك"}), 403
    
    # تحديد supplier_id
    if user_type == 'staff':
        supplier_id = current_user.supplier_id
    else:
        supplier_id = current_user.id
    
    try:
        # جلب جميع المنتجات المرتبطة بهذا المورد
        mappings = ProductSupplierMapping.query.filter_by(
            supplier_id=supplier_id,
            status='active'
        ).all()
        
        product_qids = [m.product_qid for m in mappings]
        
        # جلب بيانات المنتجات من Qumra
        sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
        products = []
        
        for qid in product_qids:
            product = sync_service.fetch_product_by_qid(qid)
            if product:
                products.append(product)
        
        return jsonify({
            "success": True,
            "message": f"تم مزامنة {len(products)} منتج بنجاح",
            "count": len(products)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"حدث خطأ أثناء المزامنة: {str(e)}"
        }), 500
