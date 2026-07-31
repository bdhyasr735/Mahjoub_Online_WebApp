# coding: utf-8
# 📂 apps/suppliers_product/routes/products.py
# (نسخة كاملة وصحيحة 100%)

import math
import traceback
from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_required
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping

def get_status_text(status):
    status_map = {
        'PUBLISHED': 'منشور',
        'DRAFT': 'مسودة',
        'ARCHIVED': 'مؤرشف',
        'PENDING': 'قيد المراجعة',
        'REJECTED': 'مرفوض',
        'OUT_OF_STOCK': 'نفد من المخزون',
        'INACTIVE': 'غير نشط'
    }
    return status_map.get(status, status)

def format_price(price):
    if price is None:
        return '0.00 ر.س'
    try:
        return f"{float(price):,.2f} ر.س"
    except:
        return str(price)

@suppliers_product_bp.route('/products', methods=['GET'], endpoint='list_supplier_products')
@login_required
def manage_supplier_products_view():
    try:
        user_type = session.get('user_type')
        supplier_id = session.get('user_id') or session.get('supplier_id')
        if user_type not in ('supplier', 'admin'):
            flash('❌ غير مصرح لك بالدخول', 'danger')
            return redirect(url_for('suppliers_dashboard_bp.dashboard'))

        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        limit = max(1, limit)
        
        search_term = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        status = request.args.get('status', '').strip()
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        is_ajax = request.args.get('ajax', '0') == '1'

        # 🔥 بناء الفلاتر وإرسالها للخدمة (الخدمة يجب أن تدعم ذلك)
        filters = {k: v for k, v in {
            'search': search_term,
            'category': category,
            'status': status,
            'min_price': min_price,
            'max_price': max_price
        }.items() if v}

        products_data = []
        total_items_all = 0
        try:
            # 🚀 جلب صفحة واحدة فقط مع الفلاتر - بدون حلقة!
            result = services.products.get_products_page(page, filters)
            if result:
                products_data = result.get('data', [])
                pagination_info = result.get('pagination', {})
                total_items_all = pagination_info.get('totalItems', 0)
        except Exception as e:
            current_app.logger.error(f"خطأ جلب المنتجات: {traceback.format_exc()}")

        target_products = []
        if products_data:
            try:
                if user_type != 'admin' and supplier_id:
                    supplier_mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
                    supplier_qids = {m.product_qid for m in supplier_mappings}
                    target_products = [p for p in products_data if p.get('qid') in supplier_qids]
                else:
                    target_products = products_data
            except Exception as e:
                current_app.logger.error(f"خطأ في التصفية: {traceback.format_exc()}")

        formatted_products = [{'product': p} for p in target_products]

        per_page = limit
        total_pages = math.ceil(total_items_all / per_page) if total_items_all > 0 else 0

        pagination_info = {
            'current_page': page,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_num': page - 1 if page > 1 else 1,
            'next_num': page + 1 if page < total_pages else page,
            'per_page': per_page,
            'total_items': total_items_all
        }

        return render_template(
            'suppliers/suppliers_product.html',
            products=formatted_products,
            pagination=pagination_info,
            get_status_text=get_status_text,
            format_price=format_price
        )

    except Exception as e:
        current_app.logger.error(f"خطأ غير متوقع: {traceback.format_exc()}")
        flash('❌ حدث خطأ غير متوقع', 'danger')
        return render_template('suppliers/suppliers_product.html', products=[], pagination={'total_pages':0, 'total_items':0}, get_status_text=get_status_text, format_price=format_price)
