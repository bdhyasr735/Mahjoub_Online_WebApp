# coding: utf-8
# 📂 apps/suppliers_product/routes/crud.py

import traceback
from flask import render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import login_required, current_user
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.extensions import db
from datetime import datetime

# ============================================================================================
# 🔍 عرض صفحة البحث عن منتجات جديدة من قمرة لربطها بالمورد
# ============================================================================================
@suppliers_product_bp.route('/products/search', methods=['GET'], endpoint='search_supplier_products')
@login_required
def search_supplier_products():
    """
    صفحة للمورد للبحث عن منتجات قمرة وإضافتها إلى متجره.
    """
    try:
        supplier_id = getattr(current_user, 'id', None) or session.get('supplier_id') or session.get('user_id')
        
        # جلب معاملات البحث والترقيم
        page = request.args.get('page', 1, type=int)
        search_term = request.args.get('search', '').strip()
        
        # جلب منتجات قمرة للصفحة الحالية
        result = services.products.get_products_page(page)
        all_products = result.get('data', [])
        pagination = result.get('pagination', {})
        
        # فلترة البحث إذا وجد
        if search_term:
            filtered = [p for p in all_products if search_term.lower() in p.get('title', '').lower()]
        else:
            filtered = all_products

        # جلب المنتجات التي ربطها المورد بالفعل لمنع ازدواجية العرض
        existing_mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
        existing_qids = {m.product_qid for m in existing_mappings}

        # إضافة علم لكل منتج هل هو مرتبط أم لا
        for p in filtered:
            p['is_linked'] = p.get('qid') in existing_qids

        return render_template(
            'suppliers/search_products.html', 
            products=filtered, 
            search_term=search_term,
            pagination=pagination
        )

    except Exception as e:
        current_app.logger.error(f"خطأ في البحث عن المنتجات: {traceback.format_exc()}")
        flash('❌ حدث خطأ أثناء تحميل منتجات البحث.', 'danger')
        return redirect(url_for('suppliers_product_bp.list_supplier_products'))


# ============================================================================================
# ➕ ربط منتج جديد للمورد (إضافة ربطة في جدول product_supplier_mapping)
# ============================================================================================
@suppliers_product_bp.route('/products/link/<string:product_qid>', methods=['POST'], endpoint='link_supplier_product')
@login_required
def link_supplier_product(product_qid):
    """
    عملية ربط منتج قمرة بالمورد الحالي.
    """
    try:
        supplier_id = getattr(current_user, 'id', None) or session.get('supplier_id') or session.get('user_id')
        
        # التحقق من عدم وجود الربط مسبقاً
        existing = ProductSupplierMapping.query.filter_by(
            supplier_id=supplier_id, 
            product_qid=product_qid
        ).first()
        
        if existing:
            flash('⚠️ هذا المنتج موجود بالفعل في قائمتك.', 'warning')
            return redirect(url_for('suppliers_product_bp.search_supplier_products'))

        # التأكد من أن المنتج موجود في قمرة
        product = services.products.get_product_by_qid(product_qid)
        if not product:
            flash('❌ المنتج غير موجود في قمرة أو تم حذفه.', 'danger')
            return redirect(url_for('suppliers_product_bp.search_supplier_products'))

        # إنشاء سجل ربط جديد
        new_mapping = ProductSupplierMapping(
            product_qid=product_qid,
            supplier_id=supplier_id,
            status='PENDING',  # الحالة الافتراضية كما طلبت: قيد المراجعة
            price=0.0,         # سعر التكلفة الافتراضي
            quantity=0         # الكمية الافتراضية
        )
        db.session.add(new_mapping)
        db.session.commit()

        flash('✅ تم ربط المنتج بنجاح، بإمكانك الآن تعديل سعر التكلفة والكمية.', 'success')
        return redirect(url_for('suppliers_product_bp.list_supplier_products'))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"خطأ في ربط المنتج: {traceback.format_exc()}")
        flash('❌ حدث خطأ غير متوقع أثناء ربط المنتج.', 'danger')
        return redirect(url_for('suppliers_product_bp.search_supplier_products'))


# ============================================================================================
# ❌ حذف منتج من قائمة المورد (إزالة الربط)
# ============================================================================================
@suppliers_product_bp.route('/products/unlink/<string:product_qid>', methods=['POST'], endpoint='unlink_supplier_product')
@login_required
def unlink_supplier_product(product_qid):
    """
    حذف الربط بين المورد والمنتج (لا يحذف المنتج من قمرة، بل يزيله فقط من قائمة المورد).
    """
    try:
        supplier_id = getattr(current_user, 'id', None) or session.get('supplier_id') or session.get('user_id')
        
        mapping = ProductSupplierMapping.query.filter_by(
            supplier_id=supplier_id, 
            product_qid=product_qid
        ).first()
        
        if not mapping:
            flash('⚠️ لا تملك الصلاحية لحذف هذا المنتج.', 'danger')
            return redirect(url_for('suppliers_product_bp.list_supplier_products'))
        
        db.session.delete(mapping)
        db.session.commit()
        
        flash('✅ تم إزالة المنتج من قائمتك بنجاح.', 'success')
        return redirect(url_for('suppliers_product_bp.list_supplier_products'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"خطأ في حذف الربط: {traceback.format_exc()}")
        flash('❌ حدث خطأ غير متوقع أثناء إزالة المنتج.', 'danger')
        return redirect(url_for('suppliers_product_bp.list_supplier_products'))


# ============================================================================================
# ✍️ دالة تسجيل مسارات CRUD (اختياري، إذا كنت تريد ربطها بـ __init__.py مثل products.py)
# ============================================================================================
def register_crud_route(bp):
    # مسار البحث عن المنتجات
    bp.add_url_rule('/products/search', view_func=search_supplier_products, methods=['GET'], endpoint='search_supplier_products')
    # مسار ربط منتج جديد
    bp.add_url_rule('/products/link/<string:product_qid>', view_func=link_supplier_product, methods=['POST'], endpoint='link_supplier_product')
    # مسار حذف منتج (فك الارتباط)
    bp.add_url_rule('/products/unlink/<string:product_qid>', view_func=unlink_supplier_product, methods=['POST'], endpoint='unlink_supplier_product')
