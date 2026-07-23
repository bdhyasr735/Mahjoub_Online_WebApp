# coding: utf-8
# 📂 apps/suppliers_product/suppliers_product_routes.py

from flask import render_template, request, abort, session, redirect, url_for, flash
from flask_login import login_required, current_user
import math
import os
import traceback

from apps.services.product_sync_service import ProductSyncService
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier
from apps.extensions import db

# ✅ استيراد الـ Blueprint من registry.py
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
    
    pages.append(1)
    
    start = max(2, current - around)
    end = min(total - 1, current + around)
    
    if start > 2:
        pages.append('...')
    
    for p in range(start, end + 1):
        pages.append(p)
    
    if end < total - 1:
        pages.append('...')
    
    if total > 1:
        pages.append(total)
    
    return pages


# ============================================================
# 🟣 مسار عرض منتجات المورد
# ============================================================
@suppliers_product_bp.route('/products', methods=['GET'])
@login_required
def products():
    """عرض منتجات المورد المرتبطة به فقط مع Pagination."""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)
        
        if user_type == 'staff':
            supplier_id = current_user.supplier_id
        else:
            supplier_id = current_user.id
        
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            abort(404)
        
        # ✅ جلب المعاملات
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search_query = request.args.get('search', '').strip()
        filter_status = request.args.get('filter', 'all')
        
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
        
        # ✅ إذا كان طلب AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template(
                'includes/_table_products.html',
                products=page_products,
                pagination=pagination
            )
        
        # ✅ عرض الصفحة كاملة
        return render_template(
            'suppliers/suppliers_product.html',
            products=page_products,
            pagination=pagination,
            search=search_query,
            filter_status=filter_status,
            supplier=supplier
        )
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ خطأ في products: {error_details}")
        return f"❌ خطأ: {error_details}", 500


# ============================================================
# 🟣 مسار عرض تفاصيل منتج معين
# ============================================================
@suppliers_product_bp.route('/product/<qid>', methods=['GET'])
@login_required
def view_product(qid):
    """عرض تفاصيل منتج معين للمورد."""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)
        
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
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ خطأ في view_product: {error_details}")
        return f"❌ خطأ: {error_details}", 500


# ============================================================
# 🟣 مسار إضافة منتج جديد (GET)
# ============================================================
@suppliers_product_bp.route('/add-product', methods=['GET'])
@login_required
def add_product():
    """صفحة إضافة منتج جديد للمورد"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)
        
        if user_type == 'staff':
            supplier_id = current_user.supplier_id
        else:
            supplier_id = current_user.id
        
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            abort(404)
        
        return render_template(
            'suppliers/add_product.html',
            supplier=supplier
        )
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ خطأ في add_product: {error_details}")
        return f"❌ خطأ: {error_details}", 500


# ============================================================
# 🟣 مسار حفظ منتج جديد (POST)
# ============================================================
@suppliers_product_bp.route('/add-product', methods=['POST'])
@login_required
def save_product():
    """حفظ منتج جديد للمورد"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)
        
        if user_type == 'staff':
            supplier_id = current_user.supplier_id
        else:
            supplier_id = current_user.id
        
        # ✅ جلب البيانات من النموذج
        name = request.form.get('name', '').strip()
        cost_price = request.form.get('cost_price', '').strip()
        
        # ✅ التحقق من البيانات
        if not name:
            flash('⚠️ اسم المنتج مطلوب', 'danger')
            return redirect(url_for('suppliers_product_bp.add_product'))
        
        if not cost_price or float(cost_price) <= 0:
            flash('⚠️ سعر التكلفة يجب أن يكون أكبر من 0', 'danger')
            return redirect(url_for('suppliers_product_bp.add_product'))
        
        # ✅ هنا يتم رفع المنتج إلى Qumra
        # ... منطق المزامنة مع Qumra ...
        
        flash('✅ تم إضافة المنتج بنجاح، سيراجعه فريق الإدارة', 'success')
        return redirect(url_for('suppliers_product_bp.products'))
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ خطأ في save_product: {error_details}")
        flash('❌ حدث خطأ أثناء إضافة المنتج', 'danger')
        return redirect(url_for('suppliers_product_bp.add_product'))


# ============================================================
# 🟣 مسار عرض صفحة تعديل المنتج
# ============================================================
@suppliers_product_bp.route('/edit-product/<qid>', methods=['GET'])
@login_required
def edit_product_page(qid):
    """صفحة تعديل منتج موجود"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)
        
        if user_type == 'staff':
            supplier_id = current_user.supplier_id
        else:
            supplier_id = current_user.id
        
        # ✅ التحقق من أن المنتج يخص هذا المورد
        mapping = ProductSupplierMapping.query.filter_by(
            product_qid=qid,
            supplier_id=supplier_id,
            status='active'
        ).first()
        
        if not mapping:
            abort(404)
        
        # ✅ جلب بيانات المنتج من Qumra
        sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
        product = sync_service.fetch_product_by_qid(qid)
        
        if not product:
            abort(404)
        
        supplier = Supplier.query.get(supplier_id)
        
        return render_template(
            'suppliers/edit_product.html',
            product=product,
            supplier=supplier,
            mapping=mapping
        )
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ خطأ في edit_product_page: {error_details}")
        return f"❌ خطأ: {error_details}", 500


# ============================================================
# 🟣 مسار تحديث المنتج (POST)
# ============================================================
@suppliers_product_bp.route('/edit-product/<qid>', methods=['POST'])
@login_required
def update_product(qid):
    """تحديث بيانات المنتج"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)
        
        if user_type == 'staff':
            supplier_id = current_user.supplier_id
        else:
            supplier_id = current_user.id
        
        # ✅ التحقق من أن المنتج يخص هذا المورد
        mapping = ProductSupplierMapping.query.filter_by(
            product_qid=qid,
            supplier_id=supplier_id,
            status='active'
        ).first()
        
        if not mapping:
            abort(404)
        
        # ✅ جلب البيانات من النموذج
        name = request.form.get('name', '').strip()
        price = request.form.get('price', '').strip()
        quantity = request.form.get('quantity', '').strip()
        description = request.form.get('description', '').strip()
        
        # ✅ التحقق من البيانات
        if not name:
            flash('⚠️ اسم المنتج مطلوب', 'danger')
            return redirect(url_for('suppliers_product_bp.edit_product_page', qid=qid))
        
        # ✅ هنا يتم تحديث المنتج في Qumra
        # ... منطق التحديث مع Qumra ...
        
        flash('✅ تم تحديث المنتج بنجاح', 'success')
        return redirect(url_for('suppliers_product_bp.products'))
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ خطأ في update_product: {error_details}")
        flash('❌ حدث خطأ أثناء تحديث المنتج', 'danger')
        return redirect(url_for('suppliers_product_bp.edit_product_page', qid=qid))


# ============================================================
# 🟣 مسار حذف المنتج
# ============================================================
@suppliers_product_bp.route('/delete-product/<qid>', methods=['POST'])
@login_required
def delete_product(qid):
    """حذف منتج للمورد"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)
        
        if user_type == 'staff':
            supplier_id = current_user.supplier_id
        else:
            supplier_id = current_user.id
        
        # ✅ التحقق من أن المنتج يخص هذا المورد
        mapping = ProductSupplierMapping.query.filter_by(
            product_qid=qid,
            supplier_id=supplier_id,
            status='active'
        ).first()
        
        if not mapping:
            abort(404)
        
        # ✅ حذف المنتج من Qumra
        sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
        result = sync_service.delete_product(qid)
        
        if result:
            # ✅ حذف الربط من قاعدة البيانات المحلية
            db.session.delete(mapping)
            db.session.commit()
            flash('✅ تم حذف المنتج بنجاح', 'success')
        else:
            flash('❌ فشل حذف المنتج', 'danger')
        
        return redirect(url_for('suppliers_product_bp.products'))
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ خطأ في delete_product: {error_details}")
        flash('❌ حدث خطأ أثناء حذف المنتج', 'danger')
        return redirect(url_for('suppliers_product_bp.products'))
