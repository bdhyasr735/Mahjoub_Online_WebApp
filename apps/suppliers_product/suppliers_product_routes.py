# coding: utf-8
# 📂 apps/suppliers_product/routes.py

import os
import json
import math
from flask import Blueprint, render_template, request, jsonify, abort, session
from flask_login import login_required, current_user
from apps.services.product_sync_service import ProductSyncService
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier
from apps.extensions import db

# ✅ استيراد الـ Blueprint من registry.py (بدلاً من تعريفه هنا)
from apps.suppliers_product.registry import suppliers_product_bp

GRAPHQL_TOKEN = os.environ.get('QUMRA_API_KEY', 'YOUR_ADMIN_API_TOKEN')


# ============================================================
# 🟣 دالة مساعدة لإنشاء بيانات الترقيم (Pagination)
# ============================================================
def get_pages_list(current, total, around=2):
    """إنشاء قائمة الصفحات مع علامات الحذف"""
    pages = []
    
    if total <= 1:
        return [1]
    
    # الصفحة الأولى
    pages.append(1)
    
    # الصفحات حول الصفحة الحالية
    start = max(2, current - around)
    end = min(total - 1, current + around)
    
    if start > 2:
        pages.append('...')
    
    for p in range(start, end + 1):
        pages.append(p)
    
    if end < total - 1:
        pages.append('...')
    
    # الصفحة الأخيرة
    if total > 1:
        pages.append(total)
    
    return pages


# ============================================================
# 🟣 مسار عرض منتجات المورد (مع Pagination والبحث والفلتر)
# ============================================================
@suppliers_product_bp.route('/products', methods=['GET'])
@login_required
def products():
    """عرض منتجات المورد المرتبطة به فقط مع Pagination."""
    
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
    
    # ✅ جلب المعاملات
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search_query = request.args.get('search', '').strip()
    filter_status = request.args.get('filter', 'all')
    view = request.args.get('view', 'grid')
    
    # ✅ جلب جميع المنتجات المرتبطة بهذا المورد
    mappings = ProductSupplierMapping.query.filter_by(
        supplier_id=supplier_id,
        status='active'
    ).all()
    
    product_qids = [m.product_qid for m in mappings]
    
    # ✅ جلب بيانات المنتجات من Qumra
    sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
    all_products = []
    
    for qid in product_qids:
        product = sync_service.fetch_product_by_qid(qid)
        if product:
            all_products.append(product)
    
    # ✅ تطبيق الفلتر حسب الحالة
    if filter_status == 'published':
        all_products = [p for p in all_products if p.get('status') == 'PUBLISHED']
    elif filter_status == 'draft':
        all_products = [p for p in all_products if p.get('status') == 'DRAFT']
    elif filter_status == 'rejected':
        all_products = [p for p in all_products if p.get('status') == 'REJECTED']
    elif filter_status == 'archived':
        all_products = [p for p in all_products if p.get('status') == 'ARCHIVED']
    
    # ✅ تطبيق البحث
    if search_query:
        all_products = [
            p for p in all_products 
            if search_query.lower() in p.get('title', '').lower() 
            or search_query.lower() in p.get('ident', {}).get('sku', '').lower()
        ]
    
    # ✅ ترتيب المنتجات (الأحدث أولاً)
    all_products.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    # ✅ Pagination
    total = len(all_products)
    total_pages = math.ceil(total / per_page) if per_page > 0 and total > 0 else 1
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = min(start + per_page, total)
    page_products = all_products[start:end] if total > 0 else []
    
    # ✅ بناء بيانات Pagination
    pagination = {
        'total': total,
        'current_page': page,
        'per_page': per_page,
        'pages': total_pages,
        'start': start + 1 if total > 0 else 0,
        'end': end,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None,
        'pages_list': get_pages_list(page, total_pages) if total_pages > 1 else [1]
    }
    
    # ✅ إذا كان طلب AJAX (للبحث أو الفلتر أو تغيير الصفحة)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # عرض البطاقات أو الجدول
        if view == 'list':
            table_html = render_template(
                'suppliers/includes/_product_table.html',
                products=page_products
            )
            pagination_html = render_template(
                'suppliers/includes/_product_pagination.html',
                pagination=pagination
            )
            return table_html + pagination_html
        else:
            cards_html = render_template(
                'suppliers/includes/_product_cards.html',
                products=page_products
            )
            pagination_html = render_template(
                'suppliers/includes/_product_pagination.html',
                pagination=pagination
            )
            return cards_html + pagination_html
    
    # ✅ عرض الصفحة كاملة (غير AJAX)
    return render_template(
        'suppliers/suppliers_product.html',
        products=page_products,
        pagination=pagination,
        search=search_query,
        filter_status=filter_status,
        view=view,
        supplier=supplier
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
        supplier=Supplier.query.get(supplier_id),
        mapping=mapping
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


# ============================================================
# 🟣 مسار تغيير حالة المنتج (للمورد)
# ============================================================
@suppliers_product_bp.route('/product/<qid>/status', methods=['POST'])
@login_required
def update_product_status(qid):
    """تحديث حالة المنتج (للإدارة فقط)."""
    
    # التحقق من أن المستخدم هو مورد
    user_type = session.get('user_type')
    if user_type not in ['supplier', 'staff']:
        return jsonify({"success": False, "message": "غير مصرح لك"}), 403
    
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
        return jsonify({"success": False, "message": "المنتج غير موجود"}), 404
    
    data = request.get_json()
    new_status = data.get('status', '').upper()
    
    if new_status not in ['PUBLISHED', 'DRAFT', 'ARCHIVED']:
        return jsonify({"success": False, "message": "حالة غير صالحة"}), 400
    
    try:
        # تحديث الحالة في Qumra
        sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
        result = sync_service.update_product_status(qid, new_status)
        
        if result:
            return jsonify({
                "success": True,
                "message": f"تم تحديث حالة المنتج إلى {new_status}",
                "status": new_status
            })
        else:
            return jsonify({
                "success": False,
                "message": "فشل تحديث حالة المنتج في Qumra"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"حدث خطأ: {str(e)}"
        }), 500
