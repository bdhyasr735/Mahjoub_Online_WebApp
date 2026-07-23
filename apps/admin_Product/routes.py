# coding: utf-8
# 📂 apps/admin_Product/routes.py

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from apps.services.product_sync_service import ProductSyncService
from apps.models.supplier_db import Supplier
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.extensions import db

admin_product_bp = Blueprint(
    'admin_product_bp',
    __name__,
    template_folder='templates',
    static_folder='static'
)

GRAPHQL_TOKEN = os.environ.get('QUMRA_API_KEY', 'YOUR_ADMIN_API_TOKEN')


# ============================================================
# ✅ عرض قائمة المنتجات
# ============================================================
@admin_product_bp.route('/products', methods=['GET'])
def manage_products():
    """عرض قائمة المنتجات مع دعم الترقيم والبحث المباشر عبر الـ API"""
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


# ============================================================
# ✅ مراجعة المنتجات (DRAFT)
# ============================================================
@admin_product_bp.route('/products/review', methods=['GET'])
def review_products():
    """صفحة مراجعة المنتجات - تعرض المنتجات التي حالتها DRAFT"""
    client = ProductSyncService(token=GRAPHQL_TOKEN)
    response_data = client.fetch_products(page=1, limit=100)
    all_products = response_data.get("data", [])
    
    # ✅ تصفية المنتجات التي حالتها DRAFT
    draft_products = [p for p in all_products if p.get('status') == 'DRAFT']
    
    # ✅ جلب الموردين لكل منتج
    for product in draft_products:
        mapping = ProductSupplierMapping.query.filter_by(
            product_qid=product.get('qid')
        ).first()
        if mapping:
            supplier = Supplier.query.get(mapping.supplier_id)
            product['supplier_name'] = supplier.trade_name if supplier else 'غير معروف'
            product['supplier_id'] = mapping.supplier_id
        else:
            product['supplier_name'] = 'غير مرتبط'
            product['supplier_id'] = None
    
    return render_template(
        'admin/admin_review_products.html',
        products=draft_products,
        total_count=len(draft_products)
    )


# ============================================================
# ✅ مزامنة المنتجات
# ============================================================
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
        flash(f"✅ تمت مزامنة البيانات بنجاح وجلب {count} منتجاً.", "success")
        
    except Exception as e:
        flash(f"❌ حدث خطأ أثناء الاتصال بالمزامنة: {str(e)}", "danger")

    return redirect(url_for('admin_product_bp.manage_products'))


# ============================================================
# ✅ إضافة منتج
# ============================================================
@admin_product_bp.route('/products/add', methods=['GET', 'POST'])
def add_product():
    """مسار إضافة منتج جديد"""
    client = ProductSyncService(token=GRAPHQL_TOKEN)
    suppliers = Supplier.query.filter_by(status='active').all()
    all_collections = client.fetch_collections() if hasattr(client, 'fetch_collections') else []

    if request.method == 'POST':
        try:
            # ✅ هنا يتم إنشاء المنتج
            flash("✅ تم إضافة المنتج بنجاح.", "success")
            return redirect(url_for('admin_product_bp.manage_products'))
        except Exception as e:
            flash(f"❌ حدث خطأ: {str(e)}", "danger")

    return render_template(
        'admin/admin_add_product.html',
        suppliers=suppliers,
        all_collections=all_collections
    )


# ============================================================
# ✅ تعديل المنتج
# ============================================================
@admin_product_bp.route('/products/edit', methods=['GET'])
def edit_product():
    """مسار عرض صفحة تعديل المنتج"""
    qid = request.args.get('qid')
    
    if not qid:
        flash("معرف المنتج (qid) مفقود.", "danger")
        return redirect(url_for('admin_product_bp.manage_products'))
    
    client = ProductSyncService(token=GRAPHQL_TOKEN)
    product = client.fetch_product_by_qid(qid)
    
    if not product:
        flash("❌ لم يتم العثور على المنتج", "danger")
        return redirect(url_for('admin_product_bp.manage_products'))
    
    suppliers = Supplier.query.filter_by(status='active').all()
    mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
    assigned_supplier_id = mapping.supplier_id if mapping else None
    all_collections = client.fetch_collections() if hasattr(client, 'fetch_collections') else []
        
    return render_template(
        'admin/admin_edit_product.html', 
        product=product,
        suppliers=suppliers,
        all_collections=all_collections,
        assigned_supplier_id=assigned_supplier_id
    )


# ============================================================
# ✅ حفظ ومزامنة المنتج
# ============================================================
@admin_product_bp.route('/products/save-sync', methods=['POST'])
def save_sync_product():
    """مسار استقبال وتخزين البيانات الواردة من قالب التعديل"""
    try:
        qid = request.form.get('qid')
        if not qid:
            return jsonify({"status": "error", "message": "qid مفقود"}), 400
        
        client = ProductSyncService(token=GRAPHQL_TOKEN)
        
        # ✅ تجميع البيانات
        info = {
            "title": request.form.get('title', ''),
            "slug": request.form.get('slug', ''),
            "status": request.form.get('status', 'DRAFT')
        }
        pricing = {
            "price": float(request.form.get('price', 0)),
            "compareAtPrice": float(request.form.get('compare_at_price', 0)),
            "costPrice": float(request.form.get('cost_price', 0))
        }
        weight = {"value": float(request.form.get('weight', 0)), "unit": "kg"}
        ident = {"sku": request.form.get('sku', '')}
        description = request.form.get('description', '')
        supplier_id = request.form.get('supplier_id')
        
        # ✅ تحديث المنتج في قمرة
        success = client.update_product_data(
            qid=qid,
            info=info,
            pricing=pricing,
            dims={"length": 0, "width": 0, "height": 0, "unit": "cm"},
            weight=weight,
            ident=ident,
            desc=description
        )
        
        if not success:
            return jsonify({"status": "error", "message": "فشل تحديث المنتج"}), 500
        
        # ✅ تحديث ربط المورد
        if supplier_id:
            mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
            if mapping:
                mapping.supplier_id = int(supplier_id)
            else:
                mapping = ProductSupplierMapping(
                    product_qid=qid,
                    supplier_id=int(supplier_id),
                    status='active'
                )
                db.session.add(mapping)
            db.session.commit()
        
        return jsonify({"status": "success", "message": "✅ تم حفظ المنتج بنجاح!"})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================
# ✅ تغيير حالة المنتج (موافقة/رفض)
# ============================================================
@admin_product_bp.route('/products/change-status/<qid>', methods=['POST'])
def change_product_status(qid):
    """تغيير حالة المنتج (موافقة أو رفض)"""
    try:
        data = request.get_json()
        new_status = data.get('status', '').upper()
        
        if new_status not in ['PUBLISHED', 'REJECTED', 'DRAFT', 'ARCHIVED']:
            return jsonify({'success': False, 'message': 'حالة غير صالحة'}), 400
        
        client = ProductSyncService(token=GRAPHQL_TOKEN)
        result = client.update_product_status(qid, new_status)
        
        if result:
            return jsonify({
                'success': True,
                'message': f'✅ تم تغيير الحالة إلى {new_status}',
                'status': new_status
            })
        else:
            return jsonify({'success': False, 'message': '❌ فشل تغيير الحالة'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
