# coding: utf-8
# 📂 apps/admin_Product/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from apps.extensions import db
from apps.models.product_db import Product

# تعريف الـ Blueprint باسم admin_product_bp ليتوافق مع url_for في القالب والـ Registry
admin_product_bp = Blueprint('admin_product_bp', __name__, template_folder='templates')


@admin_product_bp.route('/products', methods=['GET'])
@login_required
def manage_products():
    """
    عرض قائمة المنتجات الحقيقية من قاعدة البيانات مع دعم البحث والتصفح الصفحي (Pagination).
    """
    search_query = request.args.get('title', '') or request.args.get('q', '')
    search_query = search_query.strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10  # عدد المنتجات في كل صفحة

    # جلب المنتجات من قاعدة البيانات مع تطبيق البحث إن وجد
    query = Product.query
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))

    pagination_obj = query.order_by(Product.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    products = pagination_obj.items

    # هيكل بيانات الترقيم الصفحي المتوافق مع القالب
    pagination = {
        'currentPage': pagination_obj.page,
        'totalPages': pagination_obj.pages,
        'totalItems': pagination_obj.total
    }

    return render_template(
        'admin/admin_Product.html',
        products=products,
        pagination=pagination,
        search=search_query
    )


@admin_product_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """
    مسار إضافة وحفظ منتج جديد مباشرة في قاعدة البيانات مع دعم الحقول الإضافية.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description', '')
        quantity = request.form.get('quantity', 0)
        currency = request.form.get('currency', 'ر.س')
        image_url = request.form.get('image_url', '')

        if not name or not price:
            flash('يرجى إدخال اسم المنتج والسعر على الأقل.', 'danger')
            return render_template('admin/add_product.html')

        try:
            new_product = Product(
                name=name,
                price=float(price),
                description=description,
                quantity=int(quantity or 0),
                currency=currency,
                image_url=image_url
            )
            db.session.add(new_product)
            db.session.commit()

            flash('تمت إضافة وحفظ المنتج في القاعدة بنجاح!', 'success')
            return redirect(url_for('admin_product_bp.manage_products'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء حفظ المنتج في القاعدة: {str(e)}', 'danger')

    return render_template('admin/add_product.html')


@admin_product_bp.route('/products/edit/<path:qid>', methods=['GET', 'POST'])
@login_required
def edit_product(qid):
    """
    مسار تعديل وتحديث بيانات المنتج في قاعدة البيانات بناءً على الـ qid النصي الفريد.
    """
    product = Product.query.filter_by(qid=qid).first_or_404()

    if request.method == 'POST':
        product.name = request.form.get('name', product.name)
        try:
            product.price = float(request.form.get('price', product.price))
        except ValueError:
            pass
        
        try:
            product.quantity = int(request.form.get('quantity', product.quantity))
        except ValueError:
            pass

        product.currency = request.form.get('currency', product.currency)
        product.image_url = request.form.get('image_url', product.image_url)
        product.description = request.form.get('description', product.description)

        try:
            db.session.commit()
            flash('تم تحديث بيانات المنتج بنجاح!', 'success')
            return redirect(url_for('admin_product_bp.manage_products'))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء التحديث: {str(e)}', 'danger')

    return render_template('admin/edit_product.html', product=product, qid=qid)


@admin_product_bp.route('/products/sync/save', methods=['POST'])
@login_required
def save_sync():
    """
    مسار معالجة طلب المزامنة (AJAX) لجلب المنتجات وحفظها في قاعدة البيانات المحلية.
    """
    try:
        from apps.services.product_sync_service import sync_products_from_qomra
        
        # تنفيذ خدمة الجلب والحفظ الفعلي للمنتجات بكل تفاصيلها
        success_message = sync_products_from_qomra()

        return jsonify({
            'status': 'success',
            'message': success_message
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'فشل مزامنة المنتجات: {str(e)}'
        }), 500
