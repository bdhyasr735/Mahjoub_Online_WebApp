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

        # 1. استلام المتغيرات
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        limit = max(1, limit)
        
        search_term = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        status = request.args.get('status', '').strip()
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        is_ajax = request.args.get('ajax', '0') == '1'

        has_filters = any([search_term, category, status, min_price, max_price])

        # ====================================================
        # 2. منطق جلب المنتجات (مثل الأدمن تماماً: كسول وسريع)
        # ====================================================
        current_products = []
        total_items_system = 0

        if has_filters:
            # عند البحث/فلترة: نستخدم التخزين المؤقت (آمن ولا ينهار)
            # 20 صفحة = 200 منتج. يمكنك زيادتها لـ 50 إذا أردت بحثاً أعمق
            max_pages = 20 
            all_cached = services.products.fetch_all_products_for_search(max_pages=max_pages)
            # نحتاج العدد الكلي للنظام لنعرض الترقيم التقريبي
            first_res = services.products.get_products_page(1)
            if first_res:
                total_items_system = first_res.get('pagination', {}).get('totalItems', 0)
        else:
            # الحالة العادية (بدون فلاتر): نطلب صفحة واحدة فقط - سريع جداً!
            result = services.products.get_products_page(page)
            if result:
                current_products = result.get('data', [])
                pagination = result.get('pagination', {})
                total_items_system = pagination.get('totalItems', 0)

        # 3. تصفية منتجات المورد الحالي (الفلترة الأساسية)
        target_products = []
        if current_products:
            try:
                if user_type != 'admin' and supplier_id:
                    supplier_mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
                    supplier_qids = {m.product_qid for m in supplier_mappings}
                    target_products = [p for p in current_products if p.get('qid') in supplier_qids]
                else:
                    target_products = current_products
            except Exception as e:
                current_app.logger.error(f"خطأ في التصفية: {traceback.format_exc()}")

        # 4. تطبيق الفلاتر الإضافية (بحث، سعر، حالة)
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

        # ====================================================
        # 5. حساب الترقيم الذكي (تقديري وسريع جداً)
        # ====================================================
        # لو كان لدينا فلاتر، نستخدم العدد الحقيقي للمنتجات التي ظهرت
        if has_filters:
            total_items_estimate = len(filtered_products)
        else:
            # الحالة العادية: نقوم بتقدير عدد منتجات المورد
            if total_items_system > 0 and len(target_products) > 0:
                # نأخذ عينة من الصفحة الحالية لتقدير عدد المنتجات الإجمالي للمورد
                ratio = len(target_products) / len(current_products) if len(current_products) > 0 else 1
                total_items_estimate = int(total_items_system * ratio)
            else:
                total_items_estimate = len(filtered_products)

        per_page = limit
        total_pages = math.ceil(total_items_estimate / per_page) if total_items_estimate > 0 else 0
        
        # نقوم بقطع الصفحة الحالية
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paged_products = filtered_products[start_idx:end_idx]
        formatted_products = [{'product': p} for p in paged_products]

        pagination_info = {
            'current_page': page,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_num': page - 1 if page > 1 else 1,
            'next_num': page + 1 if page < total_pages else page,
            'per_page': per_page,
            'total_items': total_items_estimate
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
