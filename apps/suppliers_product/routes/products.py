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
        
        search_term = request.args.get('search', '').strip().lower()
        category = request.args.get('category', '').strip()
        status_filter = request.args.get('status', '').strip()
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        is_ajax = request.args.get('ajax', '0') == '1' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        # ====================================================
        # ✅ 2. الاستعلام المباشر عبر جدول الربط مع تفعيل الـ Pagination (لحل المشكلة من الجذور)
        # ====================================================
        mappings_query = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id)

        if status_filter:
            mappings_query = mappings_query.filter_by(status=status_filter)

        # تنفيذ التصفح الحقيقي على جدول الروابط الخاصة بهذا المورد فقط
        pagination_obj = mappings_query.paginate(page=page, per_page=limit, error_out=False)
        
        # استخراج الqid الخاصة بالصفحة الحالية فقط لطلبها لحظياً
        current_page_mappings = pagination_obj.items

        if not current_page_mappings and not is_admin:
            pagination_info = {'current_page': 1, 'total_pages': 0, 'has_prev': False, 'has_next': False, 'per_page': limit, 'total_items': 0}
            no_products_msg = "عذراً، لا توجد لديك أي منتجات مسجلة حالياً."
            
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
        # ✅ 3. الجلب اللحظي (Stateless) لمنتجات الصفحة الحالية فقط من المصدر الخارجي (قمرة)
        # ====================================================
        formatted_products = []
        
        if is_admin and not supplier_id:
            result = services.products.get_products_page(page) or {}
            target_products = result.get('data', [])
            for p in target_products:
                formatted_products.append({'product': p, 'mapping': None})
        else:
            # جمع الـ qids الخاصة بالصفحة الحالية
            qids_to_fetch = [str(m.product_qid).strip() for m in current_page_mappings if m.product_qid]
            
            if qids_to_fetch:
                # محاولة البحث وجلب المنتجات عبر فحص صفحات النظام الخارجي أو دالة مخصصة
                # (نبحث في الصفحات الخارجية للعثور على المطابقات الخاصة بالـ qids المطلوبة فقط)
                matched_dict = {}
                max_check_pages = 30
                
                for p_num in range(1, max_check_pages + 1):
                    res = services.products.get_products_page(p_num)
                    if not res or not res.get('data'):
                        break
                    for p in res.get('data', []):
                        p_qid = str(p.get('qid') or p.get('id', '')).strip()
                        if p_qid in qids_to_fetch:
                            matched_dict[p_qid] = p
                            
                    if len(matched_dict) >= len(qids_to_fetch):
                        break

                # تجميع المنتجات بناءً على ترتيب الـ mappings الأصلي مع تطبيق فلاتر البحث والترتيب
                for mapping in current_page_mappings:
                    prod_data = matched_dict.get(str(mapping.product_qid).strip())
                    if prod_data:
                        # تطبيق فلاتر البحث والفلترة الاحتياطية محلياً
                        if search_term:
                            title = str(prod_data.get('title', '')).lower()
                            sku = str(prod_data.get('sku', '')).lower()
                            if search_term not in title and search_term not in sku:
                                continue
                        
                        try:
                            price_val = float(prod_data.get('price') or prod_data.get('sale_price') or prod_data.get('regular_price') or 0)
                            if min_price and price_val < float(min_price):
                                continue
                            if max_price and price_val > float(max_price):
                                continue
                        except (ValueError, TypeError):
                            pass

                        formatted_products.append({
                            'product': prod_data,
                            'mapping': mapping
                        })

        # ====================================================
        # ✅ 4. بناء هيكل الترقيم النهائي للقالب
        # ====================================================
        pagination_info = {
            'current_page': pagination_obj.page,
            'total_pages': pagination_obj.pages,
            'has_prev': pagination_obj.has_prev,
            'has_next': pagination_obj.has_next,
            'prev_num': pagination_obj.prev_num,
            'next_num': pagination_obj.next_num,
            'per_page': pagination_obj.per_page,
            'total_items': pagination_obj.total
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
        current_app.logger.error(f"خطأ غير متوقع في إدارة منتجات المورد: {traceback.format_exc()}")
        flash('❌ حدث خطأ غير متوقع أثناء تحميل المنتجات', 'danger')
        return render_template(
            'suppliers/suppliers_product.html',
            products=[],
            pagination={'total_pages': 0, 'total_items': 0, 'current_page': 1},
            get_status_text=get_status_text,
            format_price=format_price
        )
