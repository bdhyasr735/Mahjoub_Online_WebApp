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
        # ✅ 2. جلب QIDs الخاصة بالمورد وتوحيدها كنصوص نظيفة
        # ====================================================
        supplier_qids_set = set()
        if supplier_id:
            mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
            supplier_qids_set = {str(m.product_qid).strip() for m in mappings if m.product_qid}

        # إذا لم يملك المورد أي منتجات مسجلة ولم يكن أدمن، تعاد قائمة فارغة مباشرة مع رسالة واضحة
        if not supplier_qids_set and not is_admin:
            pagination_info = {'current_page': 1, 'total_pages': 0, 'has_prev': False, 'has_next': False, 'per_page': limit, 'total_items': 0}
            no_products_msg = "عذراً، لا توجد لديك أي منتجات مسجلة حالياً. يمكنك الضغط على زر المزامنة لجلب منتجاتك."
            
            if is_ajax:
                return jsonify({
                    'success': True,
                    'html': render_template('suppliers/includes/_product_grid.html', products=[], get_status_text=get_status_text, format_price=format_price, no_products_message=no_products_msg),
                    'pagination_html': render_template('suppliers/includes/_pagination.html', pagination=pagination_info)
                })
            return render_template(
                'suppliers/suppliers_product.html', 
                products=[], 
                pagination=pagination_info, 
                get_status_text=get_status_text, 
                format_price=format_price,
                no_products_message=no_products_msg
            )

        # ====================================================
        # ✅ 3. جلب منتجات المورد الخاصة به فقط وبدقة متناهية
        # ====================================================
        target_products = []
        
        if is_admin and not supplier_id:
            result = services.products.get_products_page(page) or {}
            target_products = result.get('data', [])
            pagination = result.get('pagination', {})
            total_items_real = pagination.get('totalItems', 0)
            total_pages = pagination.get('totalPages', 1)
        else:
            all_matched_products = []
            max_check_pages = 50  # نطاق أوسع لضمان فحص جميع الصفحات وجلب منتجات المورد فقط
            
            for p_num in range(1, max_check_pages + 1):
                res = services.products.get_products_page(p_num)
                if not res or not res.get('data'):
                    break
                page_items = res.get('data', [])
                
                for p in page_items:
                    p_qid = str(p.get('qid', '')).strip()
                    # مطابقة صارمة: المنتج يجب أن يكون موجوداً في قائمة ربط هذا المورد حصراً
                    if p_qid and p_qid in supplier_qids_set:
                        all_matched_products.append(p)

            target_products = all_matched_products

        # ====================================================
        # ✅ 4. تطبيق فلاتر البحث الإضافية
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
        # ✅ 5. الترقيم المحلي لمنتجات المورد فقط
        # ====================================================
        if supplier_id or not is_admin:
            total_items_real = len(filtered_products)
            total_pages = math.ceil(total_items_real / limit) if total_items_real > 0 else 0
            
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            paged_products = filtered_products[start_idx:end_idx]
        else:
            paged_products = filtered_products

        formatted_products = [{'product': p} for p in paged_products]

        pagination_info = {
            'current_page': page,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_num': page - 1 if page > 1 else 1,
            'next_num': page + 1 if page < total_pages else page,
            'per_page': limit,
            'total_items': total_items_real
        }

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
