# coding: utf-8
# 📂 apps/suppliers_product/routes/products.py

import math
import traceback
from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_required
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping

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

@suppliers_product_bp.route('/products', methods=['GET'], endpoint='list_supplier_products')
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
        limit = request.args.get('limit', 10, type=int)
        limit = max(1, limit) # مفتوح للأعلى
        
        search_term = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        status = request.args.get('status', '').strip()
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        is_ajax = request.args.get('ajax', '0') == '1'

        # ✅ جلب صفحة واحدة فقط (Lazy Loading) - لا توجد حلقة هنا!
        all_products = []
        total_items = 0
        try:
            result = services.products.get_products_page(page)
            if result:
                all_products = result.get('data', [])
                # جلب العدد الكلي من الـ GraphQL مباشرة
                pagination_info = result.get('pagination', {})
                total_items = pagination_info.get('totalItems', 0)
        except Exception as e:
            current_app.logger.error(f"خطأ جلب المنتجات: {traceback.format_exc()}")

        # تصفية منتجات المورد الحالي (فلترة قائمة صغيرة بدلاً من الملايين)
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

        # تطبيق البحث والفلاتر (سيتم تطبيقها على الصفحة الحالية فقط، ولن تسبب انهياراً!)
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

        # حساب الترقيم (بناءً على totalItems الحقيقي القادم من الخادم)
        per_page = limit
        total_pages = math.ceil(total_items / per_page) if total_items > 0 else 0
        
        formatted_products = [{'product': p} for p in filtered_products]

        pagination_info = {
            'current_page': page,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_num': page - 1 if page > 1 else 1,
            'next_num': page + 1 if page < total_pages else page,
            'per_page': per_page,
            'total_items': total_items
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
