# -*- coding: utf-8 -*-
"""
routes.py: مسارات الـ Flask للتحكم بالمنتجات، الرفع، التعديل، والحالة لموديول admin_Product
متجر محجوب أونلاين (www.mahjoub.online)
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from . import admin_product_bp
from .services import ProductService


@admin_product_bp.route('/', methods=['GET'])
@login_required
def list_products():
    """
    واجهة جدول عرض المنتجات وتصنيفها والبحث
    """
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip()
    status = request.args.get('status', 'all', type=str)
    collection = request.args.get('collection', 'all', type=str)

    result = ProductService.get_products_page(
        page=page,
        per_page=10,
        search=search,
        status=status,
        collection=collection
    )

    collections = ProductService.get_collections()

    return render_template(
        'admin_Product/products_list.html',
        products=result.get('products', []),
        pagination=result,
        search=search,
        selected_status=status,
        selected_collection=collection,
        collections=collections
    )


@admin_product_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_product():
    """
    نافذة/صفحة رفع وإضافة منتج جديد مع المتغيرات والـ SEO
    """
    if request.method == 'POST':
        try:
            data = {
                "title": request.form.get('title'),
                "slug": request.form.get('slug') or ProductService.generate_slug(request.form.get('title', '')),
                "status": request.form.get('status', 'draft'),
                "description": request.form.get('description'),
                "price": float(request.form.get('price', 0)),
                "compareAtPrice": float(request.form.get('compareAtPrice')) if request.form.get('compareAtPrice') else None,
                "quantity": int(request.form.get('quantity', 0)),
                "sku": request.form.get('sku'),
                "barcode": request.form.get('barcode'),
                "collections": request.form.getlist('collections'),
                "tags": [t.strip() for t in request.form.get('tags', '').split(',') if t.strip()],
                "images": [{"fileUrl": request.form.get('main_image_url'), "isMain": True}] if request.form.get('main_image_url') else [],
                "seo": {
                    "title": request.form.get('seo_title'),
                    "description": request.form.get('seo_description'),
                    "canonicalUrl": request.form.get('seo_canonical')
                },
                "dynamic_variants": []
            }

            if not data["title"]:
                flash("يرجى إدخال عنوان المنتج الأساسي.", "danger")
                return redirect(url_for('admin_Product.create_product'))

            ProductService.create_product_data(data)

            flash("تم إضافة المنتج بنجاح إلى متجر محجوب أونلاين!", "success")
            return redirect(url_for('admin_Product.list_products'))

        except Exception as e:
            flash(f"حدث خطأ أثناء حفظ المنتج: {str(e)}", "danger")
            return redirect(url_for('admin_Product.create_product'))

    collections = ProductService.get_collections()
    available_tags = ProductService.get_tags()
    return render_template('admin_Product/product_form.html', product=None, collections=collections, tags=available_tags)


@admin_product_bp.route('/<product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """
    نافذة/صفحة تعديل منتج موجود
    """
    product = ProductService.get_product_by_id(product_id)
    if not product:
        flash("المنتج المطلوب غير موجود!", "warning")
        return redirect(url_for('admin_Product.list_products'))

    if request.method == 'POST':
        try:
            data = {
                "title": request.form.get('title'),
                "slug": request.form.get('slug'),
                "status": request.form.get('status'),
                "description": request.form.get('description'),
                "price": float(request.form.get('price', 0)),
                "compareAtPrice": float(request.form.get('compareAtPrice')) if request.form.get('compareAtPrice') else None,
                "quantity": int(request.form.get('quantity', 0)),
                "sku": request.form.get('sku'),
                "barcode": request.form.get('barcode'),
                "collections": request.form.getlist('collections'),
                "tags": [t.strip() for t in request.form.get('tags', '').split(',') if t.strip()],
                "seo": {
                    "title": request.form.get('seo_title'),
                    "description": request.form.get('seo_description'),
                    "canonicalUrl": request.form.get('seo_canonical')
                }
            }

            ProductService.update_product_data(product_id, data)

            flash("تم تحديث بيانات المنتج بنجاح!", "success")
            return redirect(url_for('admin_Product.list_products'))

        except Exception as e:
            flash(f"خطأ في تحديث البيانات: {str(e)}", "danger")
            return redirect(url_for('admin_Product.edit_product', product_id=product_id))

    collections = ProductService.get_collections()
    available_tags = ProductService.get_tags()
    return render_template('admin_Product/product_form.html', product=product, collections=collections, tags=available_tags)


@admin_product_bp.route('/<product_id>/status', methods=['GET', 'POST'])
@login_required
def toggle_status(product_id):
    """
    تغيير حالة المنتج (نشط / مسودة / مؤرشف) - يدعم GET و POST لمنع خطأ Method Not Allowed
    """
    new_status = request.form.get('status') or request.args.get('status')
    
    if not new_status:
        flash("لم يتم تحديد الحالة الجديدة للمنتج.", "warning")
        return redirect(url_for('admin_Product.list_products'))

    success, _ = ProductService.toggle_product_status(product_id, new_status)
    if success:
        flash("تم تحديث حالة المنتج بنجاح.", "info")
    else:
        flash("تعذر تحديث حالة المنتج.", "danger")

    return redirect(url_for('admin_Product.list_products'))


@admin_product_bp.route('/api/generate-slug', methods=['POST'])
@login_required
def generate_slug_api():
    """توليد slug تلقائياً عبر الطلب"""
    data = request.get_json() or {}
    title = data.get('title', '')
    slug = ProductService.generate_slug(title)
    return jsonify({"slug": slug})
