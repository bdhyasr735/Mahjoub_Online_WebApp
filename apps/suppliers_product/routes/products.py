# coding: utf-8
# 📂 apps/suppliers_product/routes/products.py

import math
import traceback
from flask import render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import login_required, current_user
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
        # ✅ 1. التحقق الآمن من هُوية المورد وصلاحيات الدخول
        supplier_id = getattr(current_user, 'id', None) or session.get('supplier_id') or session.get('user_id') or session.get('_user_id')
        user_type = getattr(current_user, 'user_type', None) or getattr(current_user, 'role', None) or session.get('user_type')

        is_admin = (user_type == 'admin' or getattr(current_user, 'is_admin', False))

        if user_type not in ('supplier', 'admin') and not is_admin:
            flash('❌ غير مصرح لك بالدخول', 'danger')
            return redirect(url_for('suppliers_dashboard_bp.dashboard'))

        # استلام متغيرات التصفية والترقيم
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        limit = max(1, limit)
        
        search_term = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        status = request.args.get('status', '').strip()
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        is_ajax = request.args.get('ajax', '0') == '1'

        # ====================================================
        # ✅ 2. جلب QIDs الخاصة بالمورد مع تحويلها لنصوص لضمان المقارنة
        # ====================================================
        supplier_qids = []
        if supplier_id:
            mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
            supplier_qids = [str(m.product_qid).strip() for m in mappings if m.product_qid]
        
        supplier_qids_set = set(supplier_qids)

        # ====================================================
        # ✅ 3. جلب المنتجات وتطبيق الفلترة الصارمة على المورد
        # ====================================================
        target_products = []
        
        # إذا لم يملك المورد أي منتجات مسجلة في قاعدة البيانات المحلية ولم يكن أدمن، تعاد قائمة فارغة مباشرة
        if not supplier_qids_set and not is_admin:
            target_products = []
        else:
            # جلب المنتجات من API النظام الخارجي
            max_pages = 20
            raw_products = services.products.fetch_all_products_for_search(max_pages=max_pages) or []

            if is_admin and not supplier_id:
                target_products = raw_products  # للأدمن فقط إذا لم يُحدد مورد
            else:
                # تصفية حصرية: الاحتفاظ بالمنتجات التي تطابق QID الخاص بالمورد فقط
                target_products = [
                    p for p in raw_products 
                    if str(p.get('qid', '')).strip() in supplier_qids_set
                ]

        # ====================================================
        # ✅ 4. تطبيق فلاتر البحث الإضافية (الاسم/SKU، الفئة، الحالة، السعر)
        # ====================================================
        filtered_products = []
        for p in target_products:
            if search_term:
                title = str(p.get('title', '')).lower()
                sku = str(p.get('sku', '')).lower()
                if search_term.lower() not in title and search_term.lower() not in sku:
                    continue
            if category and p.get('category') != category:
                continue
            if status and p.get('status') != status:
                continue
            try:
                price_val = float(p.get('price') or p.get('sale_price') or p.get('regular_price') or 0)
                if min_price and price_val < float(min_price):
                    continue
                if max_price and price_val > float(max_price):
                    continue
            except (ValueError, TypeError):
                pass
            
            filtered_products.append(p)

        # ====================================================
        # ✅ 5. حساب الترقيم وتجهيز الصفحة
        # ====================================================
        total_items_real = len(filtered_products)
        per_page = limit
        total_pages = math.ceil(total_items_real / per_page) if total_items_real > 0 else 0

        # تقطيع المنتجات لعرض الصفحة الحالية فقط
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

        # استجابة AJAX للمزامنة والفلترة الفورية
        if is_ajax:
            return jsonify({
                'success': True,
                'html': render_template(
                    'suppliers/includes/_product_grid.html',
                    products=formatted_products,
                    get_status_text=get_status_text,
                    format_price=format_price
                ),
                'pagination_html': render_template(
                    'suppliers/includes/_pagination.html',
                    pagination=pagination_info
                )
            })

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
        return render_template(
            'suppliers/suppliers_product.html',
            products=[],
            pagination={'total_pages': 0, 'total_items': 0, 'current_page': 1},
            get_status_text=get_status_text,
            format_price=format_price
        )
