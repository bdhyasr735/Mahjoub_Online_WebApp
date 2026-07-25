# coding: utf-8
# 📂 apps/suppliers_product/product_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .helpers import (
    paginate,
    filter_by_search,
    filter_by_status,
    get_status_badge,
    get_status_text,
    extract_product_data,
    format_price,
    generate_sku,
    validate_product_data,
    get_product_stats_from_list,
    compress_image
)
import logging

logger = logging.getLogger(__name__)

suppliers_product_bp = Blueprint(
    'suppliers_product',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/supplier/product'
)


@suppliers_product_bp.route('/')
def index():
    """
    عرض قائمة منتجات الموردين مع دعم الترقيم، البحث، والتصفية حسب الحالة
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '', type=str)
        status = request.args.get('status', 'all', type=str)

        # جلب البيانات الأساسية (يمكن استبدالها لاحقاً بالاستعلام الفعلي من قاعدة البيانات أو GraphQL)
        products = [] 

        # تطبيق الفلاتر والبحث
        filtered_products = filter_by_search(products, search)
        filtered_products = filter_by_status(filtered_products, status)

        # حساب الإحصائيات
        stats = get_product_stats_from_list(products)
        
        # استخراج القيم بشكل فردي لتتوافق مع القالب
        total_products = stats.get('total', 0) if isinstance(stats, dict) else len(products)
        active_products = stats.get('active', 0) if isinstance(stats, dict) else 0
        draft_products = stats.get('draft', 0) if isinstance(stats, dict) else 0

        # تطبيق الترقيم
        pagination_data = paginate(filtered_products, page=page, per_page=per_page)

        return render_template(
            'suppliers/suppliers_product.html',
            products=pagination_data,  # تم تمريرها باسم products لتعمل مع products.items في القالب
            total_products=total_products,
            active_products=active_products,
            draft_products=draft_products,
            search=search,
            current_status=status,
            get_status_badge=get_status_badge,
            get_status_text=get_status_text,
            format_price=format_price
        )
    except Exception as e:
        logger.error(f"❌ خطأ في عرض قائمة منتجات الموردين: {e}")
        flash('حدث خطأ أثناء تحميل المنتجات', 'danger')
        return redirect(url_for('suppliers_product.index'))


@suppliers_product_bp.route('/add', methods=['GET', 'POST'])
def add_product():
    """
    إضافة منتج جديد للمورد
    """
    if request.method == 'POST':
        data = {
            'title': request.form.get('title'),
            'price': request.form.get('price'),
            'quantity': request.form.get('quantity'),
            'sku': request.form.get('sku') or generate_sku(),
            'description': request.form.get('description'),
            'status': request.form.get('status', 'DRAFT')
        }

        is_valid, errors = validate_product_data(data)
        if not is_valid:
            for error in errors:
                flash(error, 'danger')
            return render_template('suppliers/suppliers_product.html', form_data=data, generated_sku=data['sku'])

        try:
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    image_bytes = file.read()
                    compressed_bytes = compress_image(image_bytes)

            flash('تم إضافة المنتج بنجاح', 'success')
            return redirect(url_for('suppliers_product.index'))
        except Exception as e:
            logger.error(f"❌ خطأ أثناء إضافة المنتج: {e}")
            flash('حدث خطأ أثناء حفظ المنتج', 'danger')

    return render_template('suppliers/suppliers_product.html', generated_sku=generate_sku())


@suppliers_product_bp.route('/edit/<qid>', methods=['GET', 'POST'])
def edit_product(qid):
    """
    تعديل منتج موجود
    """
    product = {}
    
    if request.method == 'POST':
        data = {
            'title': request.form.get('title'),
            'price': request.form.get('price'),
            'quantity': request.form.get('quantity'),
            'sku': request.form.get('sku'),
            'description': request.form.get('description'),
            'status': request.form.get('status', 'DRAFT')
        }

        is_valid, errors = validate_product_data(data)
        if not is_valid:
            for error in errors:
                flash(error, 'danger')
            return render_template('suppliers/suppliers_product.html', product=product)

        try:
            flash('تم تحديث المنتج بنجاح', 'success')
            return redirect(url_for('suppliers_product.index'))
        except Exception as e:
            logger.error(f"❌ خطأ أثناء تحديث المنتج {qid}: {e}")
            flash('حدث خطأ أثناء تحديث المنتج', 'danger')

    return render_template('suppliers/suppliers_product.html', product=product)


@suppliers_product_bp.route('/delete/<qid>', methods=['POST'])
def delete_product(qid):
    """
    حذف منتج
    """
    try:
        flash('تم حذف المنتج بنجاح', 'success')
    except Exception as e:
        logger.error(f"❌ خطأ أثناء حذف المنتج {qid}: {e}")
        flash('حدث خطأ أثناء حذف المنتج', 'danger')
    return redirect(url_for('suppliers_product.index'))
