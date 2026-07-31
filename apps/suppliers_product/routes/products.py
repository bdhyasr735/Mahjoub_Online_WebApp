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
        # 2. جلب معرفات المنتجات الخاصة بالمورد (QIDs) من قاعدة البيانات المحلية
        # ====================================================
        supplier_qids = []
        if supplier_id:
            mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
            supplier_qids = [m.product_qid for m in mappings]
        
        supplier_qids_set = set(supplier_qids) if supplier_qids else None

        # ====================================================
        # 3. منطق جلب المنتجات من GraphQL (بناءً على الصفحة)
        # ====================================================
        raw_products = []
        total_items_system = 0
        
        if has_filters:
            # في حالة البحث أو الفلاتر: نستخدم التخزين المؤقت الآمن (20 صفحة كحد أقصى)
            max_pages = 20
            raw_products = services.products.fetch_all_products_for_search(max_pages=max_pages)
            first_res = services.products.get_products_page(1)
            if first_res:
                total_items_system = first_res.get('pagination', {}).get('totalItems', 0)
        else:
            # بدون فلاتر: نجلب صفحة واحدة فقط (سريع جدًا)
            result = services.products.get_products_page(page)
            if result:
                raw_products = result.get('data', [])
                pagination = result.get('pagination', {})
                total_items_system = pagination.get('totalItems', 0)

        # ====================================================
        # 4. تصفية المنتجات: نحتفظ فقط بمنتجات هذا المورد
        # ====================================================
        target_products = []
        if raw_products and supplier_qids_set is not None:
            target_products = [p for p in raw_products if p.get('qid') in supplier_qids_set]
        elif raw_products:
            target_products = raw_products  # في حالة الأدمن (بدون فلترة مورد)

        # ====================================================
        # 5. تطبيق الفلاتر الإضافية (بحث، فئة، سعر، حالة)
        # ====================================================
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
        # 6. حساب العدد الإجمالي للمنتجات الخاصة بهذا المورد
        # ====================================================
        # إذا لم يكن هناك فلاتر، العدد الإجمالي هو عدد القيم في مجموعة الـ QIDs
        if not has_filters:
            if supplier_qids_set is not None:
                total_items_real = len(supplier_qids_set)
            else:
                total_items_real = len(target_products)
        else:
            # إذا كان هناك فلاتر، نعتمد على النتائج المصفاة
            total_items_real = len(filtered_products)

        # ====================================================
        # 7. تطبيق الترقيم (على قائمة المنتجات الكاملة لهذا المورد)
        # ====================================================
        per_page = limit
        total_pages = math.ceil(total_items_real / per_page) if total_items_real > 0 else 0

        # قطع الصفحة الحالية
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
            'total_items': total_items_real
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
