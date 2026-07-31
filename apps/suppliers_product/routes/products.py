# coding: utf-8
# 📂 apps/suppliers_product/routes/products.py

import math
import traceback
from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_required
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping

# ===== دوال مساعدة للقالب =====
def get_status_text(status):
    status_map = {
        'PUBLISHED': 'منشور', 'DRAFT': 'مسودة', 'ARCHIVED': 'مؤرشف',
        'PENDING': 'قيد المراجعة', 'REJECTED': 'مرفوض',
        'OUT_OF_STOCK': 'نفد من المخزون', 'INACTIVE': 'غير نشط'
    }
    return status_map.get(status, status)

def format_price(price):
    if price is None: return '0.00 ر.س'
    try: return f"{float(price):,.2f} ر.س"
    except: return str(price)


@suppliers_product_bp.route('/products', methods=['GET'])
@login_required
def manage_supplier_products_view():
    try:
        user_type = session.get('user_type')
        supplier_id = session.get('user_id') or session.get('supplier_id')
        if user_type not in ('supplier', 'admin'):
            flash('❌ غير مصرح لك بالدخول', 'danger')
            return redirect(url_for('suppliers_dashboard_bp.dashboard'))

        # استلام المتغيرات
        page = request.args.get('page', 1, type=int)
        search_term = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        status = request.args.get('status', '').strip()
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        is_ajax = request.args.get('ajax', '0') == '1'

        # جلب جميع المنتجات (لأننا سنقوم بالفلترة يدوياً)
        all_products = []
        try:
            result = services.products.get_all_products()
            if result and isinstance(result, dict): all_products = result.get('data', [])
            elif isinstance(result, list): all_products = result
        except Exception as e:
            current_app.logger.error(f"خطأ جلب المنتجات: {traceback.format_exc()}")

        # تصفية منتجات المورد الحالي
        target_products = []
        if all_products:
            try:
                if user_type != 'admin' and supplier_id:
                    supplier_mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
                    supplier_qids = {m.product_qid for m in supplier_mappings}
                    target_products = [p for p in all_products if p.get('qid') in supplier_qids]
                else:
                    target_products = all_products
            except Exception as e:
                current_app.logger.error(f"خطأ في التصفية: {traceback.format_exc()}")

        # تطبيق البحث والفلاتر
        filtered_products = []
        for p in target_products:
            if search_term:
                title = str(p.get('title', '')).lower()
                sku = str(p.get('sku', '')).lower()
                if search_term.lower() not in title and search_term.lower() not in sku: continue
            if category and p.get('category') != category: continue
            if status and p.get('status') != status: continue
            try:
                price_val = float(p.get('price') or p.get('sale_price') or p.get('regular_price') or 0)
                if min_price and price_val < float(min_price): continue
                if max_price and price_val > float(max_price): continue
            except: pass
            filtered_products.append(p)

        # تطبيق الترقيم
        per_page = 10
        total_items = len(filtered_products)
        total_pages = math.ceil(total_items / per_page) if total_items > 0 else 0
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paged_products = filtered_products[start_idx:end_idx]
        formatted_products = [{'product': p} for p in paged_products]

        # معلومات الترقيم (نبسطها للقالب)
        pagination_info = {
            'current_page': page,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_num': page - 1 if page > 1 else 1,
            'next_num': page + 1 if page < total_pages else page
        }

        return render_template(
            'suppliers/suppliers_product.html',
            products=formatted_products,
            pagination=pagination_info,  # تم تمرير معلومات الترقيم بشكل منفصل
            get_status_text=get_status_text,
            format_price=format_price
        )

    except Exception as e:
        current_app.logger.error(f"خطأ غير متوقع: {traceback.format_exc()}")
        flash('❌ حدث خطأ غير متوقع', 'danger')
        return render_template('suppliers/suppliers_product.html', products=[], pagination={'total_pages':0}, get_status_text=get_status_text, format_price=format_price)
