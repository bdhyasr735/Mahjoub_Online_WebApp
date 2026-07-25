# coding: utf-8
# 📂 apps/suppliers_product/product_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import math
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


class PaginationWrapper:
    """مساعد ذكي لتغليف الترقيم وتوفير كافة الخصائص المطلوبة للقالب الديناميكي"""
    def __init__(self, items, page=1, per_page=20, total=0):
        self.total = total if total > 0 else (len(items) if isinstance(items, list) else 0)
        self.per_page = per_page if per_page > 0 else 20
        self.pages = math.ceil(self.total / self.per_page) if self.per_page > 0 else 1
        self.current_page = max(1, min(page, self.pages)) if self.pages > 0 else 1
        
        # تقسيم العناصر إذا كانت القائمة كاملة
        if isinstance(items, (list, tuple)):
            start_idx = (self.current_page - 1) * self.per_page
            end_idx = start_idx + self.per_page
            self.items = items[start_idx:end_idx]
        elif hasattr(items, 'items'):
            self.items = items.items
        else:
            self.items = []

        self.has_prev = self.current_page > 1
        self.has_next = self.current_page < self.pages
        self.prev_page = self.current_page - 1 if self.has_prev else None
        self.next_page = self.current_page + 1 if self.has_next else None
        
        self.start = ((self.current_page - 1) * self.per_page) + 1 if self.total > 0 else 0
        self.end = min(self.current_page * self.per_page, self.total)
        
        # توليد قائمة أرقام الصفحات مع النقاط (...)
        self.pages_list = self._generate_pages_list()

    def _generate_pages_list(self):
        if self.pages <= 7:
            return list(range(1, self.pages + 1))
        
        pages = []
        pages.append(1)
        
        if self.current_page > 3:
            pages.append('...')
            
        start = max(2, self.current_page - 1)
        end = min(self.pages - 1, self.current_page + 1)
        
        for i in range(start, end + 1):
            pages.append(i)
            
        if self.current_page < self.pages - 2:
            pages.append('...')
            
        if self.pages > 1:
            pages.append(self.pages)
            
        return pages


@suppliers_product_bp.route('/')
def index():
    """
    عرض قائمة منتجات الموردين مع دعم الترقيم، البحث الديناميكي، والتصفية
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)
    
    # دعم كل من معاملات filter و status للتوافق التام
    current_filter = request.args.get('filter') or request.args.get('status', 'all', type=str)

    # جلب البيانات الأساسية للمنتجات (يمكن استبدالها بالاستعلام الفعلي من قاعدة البيانات)
    products_list = []  

    # حساب العدادات لكل حالة لتغذية أزرار الفلتر
    search_filtered_for_counts = filter_by_search(products_list, search)
    
    counts = {
        'all': len(search_filtered_for_counts),
        'active': len([p for p in search_filtered_for_counts if p.get('status') == 'ACTIVE']),
        'inactive': len([p for p in search_filtered_for_counts if p.get('status') == 'INACTIVE']),
        'out_of_stock': len([p for p in search_filtered_for_counts if p.get('quantity', 0) == 0])
    }

    # تطبيق البحث والتصفية الأساسية
    filtered_products = filter_by_search(products_list, search)
    
    if current_filter == 'active':
        filtered_products = [p for p in filtered_products if p.get('status') == 'ACTIVE']
    elif current_filter == 'inactive':
        filtered_products = [p for p in filtered_products if p.get('status') == 'INACTIVE']
    elif current_filter == 'out_of_stock':
        filtered_products = [p for p in filtered_products if p.get('quantity', 0) == 0]

    # تغليف النتائج بنظام الترقيم المطور
    pagination_data = PaginationWrapper(filtered_products, page=page, per_page=per_page)

    return render_template(
        'suppliers/suppliers_product.html',
        products=pagination_data,
        counts=counts,
        search=search,
        current_filter=current_filter,
        get_status_badge=get_status_badge,
        get_status_text=get_status_text,
        format_price=format_price
    )


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
            return render_template(
                'suppliers/add_product.html',
                form_data=data,
                generated_sku=data['sku'],
                get_status_badge=get_status_badge,
                get_status_text=get_status_text,
                format_price=format_price
            )

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

    return render_template(
        'suppliers/add_product.html',
        generated_sku=generate_sku(),
        get_status_badge=get_status_badge,
        get_status_text=get_status_text,
        format_price=format_price
    )


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
            return render_template(
                'suppliers/edit_product.html',
                product=product,
                get_status_badge=get_status_badge,
                get_status_text=get_status_text,
                format_price=format_price
            )

        try:
            flash('تم تحديث المنتج بنجاح', 'success')
            return redirect(url_for('suppliers_product.index'))
        except Exception as e:
            logger.error(f"❌ خطأ أثناء تحديث المنتج {qid}: {e}")
            flash('حدث خطأ أثناء تحديث المنتج', 'danger')

    return render_template(
        'suppliers/edit_product.html',
        product=product,
        get_status_badge=get_status_badge,
        get_status_text=get_status_text,
        format_price=format_price
    )


@suppliers_product_bp.route('/delete/<qid>', methods=['POST', 'DELETE'])
def delete_product(qid):
    """
    حذف منتج (يدعم الطلبات العادية وطلبات الـ AJAX)
    """
    try:
        # منطق الحذف الفعلي هنا
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'تم حذف المنتج بنجاح'})
            
        flash('تم حذف المنتج بنجاح', 'success')
    except Exception as e:
        logger.error(f"❌ خطأ أثناء حذف المنتج {qid}: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 400
        flash('حدث خطأ أثناء حذف المنتج', 'danger')
        
    return redirect(url_for('suppliers_product.index'))
