# coding: utf-8
# 📂 apps/admin_Product/routes.py

"""
routes.py: مسارات الـ Flask للتحكم بالمنتجات، الرفع، التعديل، والـ API الخاصة بموديول admin_Product
متجر محجوب أونلاين (www.mahjoub.online)
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from . import admin_product_bp
from .services import ProductService

@admin_product_bp.route('/', methods=['GET'])
def list_products():
    """
    واجهة جدول عرض المنتجات وتصنيفها والبحث
    """
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
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
        products=result['products'],
        pagination=result['pagination'],  # <-- تم التصحيح هنا ليمرر بيانات الـ pagination بشكل مباشر للقالب
        search=search,
        selected_status=status,
        selected_collection=collection,
        collections=collections
    )

@admin_product_bp.route('/create', methods=['GET', 'POST'])
def create_product():
    """
    نافذة/صفحة رفع وإضافة منتج جديد مع المتغيرات والـ SEO
    """
    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json()
            else:
                data = {
                    "title": request.form.get('title'),
                    "slug": request.form.get('slug'),
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

            new_prod = ProductService.create_product_data(data)

            if request.is_json:
                return jsonify({"success": True, "message": "تم إضافة المنتج بنجاح", "product": new_prod}), 201

            flash("تم إضافة المنتج بنجاح إلى متجر محجوب أونلاين!", "success")
            return redirect(url_for('admin_Product.list_products'))

        except Exception as e:
            if request.is_json:
                return jsonify({"success": False, "error": str(e)}), 400
            flash(f"حدث خطأ أثناء حفظ المنتج: {str(e)}", "danger")

    collections = ProductService.get_collections()
    available_tags = ProductService.get_tags()
    return render_template('admin_Product/product_form.html', product=None, collections=collections, tags=available_tags)

@admin_product_bp.route('/<product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    """
    نافذة/صفحة تعديل منتج موجود
    """
    product = ProductService.get_product_by_id(product_id)
    if not product:
        if request.is_json:
            return jsonify({"success": False, "error": "المنتج غير موجود"}), 404
        flash("المنتج المطلوب غير موجود!", "warning")
        return redirect(url_for('admin_Product.list_products'))

    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json()
            else:
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

            updated = ProductService.update_product_data(product_id, data)

            if request.is_json:
                return jsonify({"success": True, "message": "تم تحديث المنتج بنجاح", "product": updated})

            flash("تم تحديث بيانات المنتج بنجاح!", "success")
            return redirect(url_for('admin_Product.list_products'))

        except Exception as e:
            if request.is_json:
                return jsonify({"success": False, "error": str(e)}), 400
            flash(f"خطأ في تحديث البيانات: {str(e)}", "danger")

    collections = ProductService.get_collections()
    available_tags = ProductService.get_tags()
    return render_template('admin_Product/product_form.html', product=product, collections=collections, tags=available_tags)

@admin_product_bp.route('/<product_id>/delete', methods=['POST'])
def delete_product(product_id):
    """
    حذف منتج
    """
    success, deleted = ProductService.delete_product_data(product_id)
    if request.is_json:
        if success:
            return jsonify({"success": True, "message": "تم حذف المنتج بنجاح"})
        return jsonify({"success": False, "error": "المنتج غير موجود"}), 404

    if success:
        flash("تم حذف المنتج بنجاح.", "success")
    else:
        flash("فشل في حذف المنتج.", "danger")

    return redirect(url_for('admin_Product.list_products'))

@admin_product_bp.route('/<product_id>/status', methods=['POST'])
def toggle_status(product_id):
    """
    تغيير حالة المنتج (نشط / مسودة / مؤرشف)
    """
    new_status = request.form.get('status') or (request.json.get('status') if request.is_json else None)
    if not new_status:
        return jsonify({"success": False, "error": "الحالة غير محددة"}), 400

    success, product = ProductService.toggle_product_status(product_id, new_status)
    if request.is_json:
        if success:
            return jsonify({"success": True, "message": "تم تغيير حالة المنتج بنجاح", "product": product})
        return jsonify({"success": False, "error": "المنتج غير موجود"}), 404

    flash("تم تحديث حالة المنتج.", "info")
    return redirect(url_for('admin_Product.list_products'))

@admin_product_bp.route('/api/generate-slug', methods=['POST'])
def generate_slug_api():
    """توليد slug تلقائياً عبر AJAX"""
    data = request.get_json() or {}
    title = data.get('title', '')
    slug = ProductService.generate_slug(title)
    return jsonify({"slug": slug})
