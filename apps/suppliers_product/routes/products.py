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
        supplier_id = getattr(current_user, 'id', None) or session.get('supplier_id') or session.get('user_id') or session.get('_user_id')
        user_type = getattr(current_user, 'user_type', None) or getattr(current_user, 'role', None) or session.get('user_type')

        is_admin = (user_type == 'admin' or getattr(current_user, 'is_admin', False))

        if user_type not in ('supplier', 'admin') and not is_admin:
            flash('❌ غير مصرح لك بالدخول', 'danger')
            return redirect(url_for('suppliers_dashboard_bp.dashboard'))

        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        limit = max(1, limit)
        
        search_term = request.args.get('search', '').strip().lower()
        category = request.args.get('category', '').strip()
        status_filter = request.args.get('status', '').strip()
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        is_ajax = request.args.get('ajax', '0') == '1' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        mappings_query = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id)

        if status_filter:
            mappings_query = mappings_query.filter_by(status=status_filter)

        pagination_obj = mappings_query.paginate(page=page, per_page=limit, error_out=False)
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

        formatted_products = []
        
        if is_admin and not supplier_id:
            result = services.products.get_products_page(page) or {}
            target_products = result.get('data', [])
            for p in target_products:
                formatted_products.append({'product': p, 'mapping': None})
        else:
            qids_to_fetch = [str(m.product_qid).strip() for m in current_page_mappings if m.product_qid]
            
            if qids_to_fetch:
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

                for mapping in current_page_mappings:
                    prod_data = matched_dict.get(str(mapping.product_qid).strip())
                    if prod_data:
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


@suppliers_product_bp.route('/products/edit/<path:qid>', methods=['GET'], endpoint='edit_supplier_product')
@login_required
def edit_product_view(qid):
    """عرض صفحة تعديل المنتج مع جلب بياناته الأساسية"""
    try:
        # تنظيف qid ليكون فقط الجزء الأخير (الرقم أو المعرف الصافي)
        clean_qid = str(qid).strip()
        if 'Product/' in clean_qid:
            clean_qid = clean_qid.split('Product/')[-1]
        while clean_qid and clean_qid.startswith('qid:'):
            clean_qid = clean_qid.replace('qid:', '', 1)
        clean_qid = clean_qid.replace('//', '').strip('/')

        supplier_id = getattr(current_user, 'id', None) or session.get('supplier_id') or session.get('user_id') or session.get('_user_id')
        user_type = getattr(current_user, 'user_type', None) or getattr(current_user, 'role', None) or session.get('user_type')
        is_admin = (user_type == 'admin' or getattr(current_user, 'is_admin', False))

        if not is_admin:
            # استخدام ilike بدلاً من filter_by للسماح بالتطابق الجزئي
            mapping = ProductSupplierMapping.query.filter(
                ProductSupplierMapping.supplier_id == supplier_id,
                ProductSupplierMapping.product_qid.ilike(f'%{clean_qid}%')
            ).first()

            if not mapping:
                flash('❌ غير مصرح لك بتعديل هذا المنتج أو المنتج غير موجود', 'danger')
                return redirect(url_for('suppliers_product_bp.list_supplier_products'))

        product_data = None
        max_check_pages = 30
        for p_num in range(1, max_check_pages + 1):
            res = services.products.get_products_page(p_num)
            if not res or not res.get('data'):
                break
            for p in res.get('data', []):
                p_current_qid = str(p.get('qid') or p.get('id', '')).strip()
                # البحث في API بالمعرف الصافي
                if clean_qid in p_current_qid or p_current_qid.endswith(clean_qid):
                    product_data = p
                    break
            if product_data:
                break

        if not product_data:
            flash('❌ لم يتم العثور على بيانات المنتج في النظام الخارجي', 'danger')
            return redirect(url_for('suppliers_product_bp.list_supplier_products'))

        return render_template(
            'suppliers/edit/base_edit.html',
            product=product_data,
            get_status_text=get_status_text,
            format_price=format_price
        )

    except Exception as e:
        current_app.logger.error(f"خطأ في عرض صفحة تعديل المنتج: {traceback.format_exc()}")
        flash('❌ حدث خطأ أثناء تحميل صفحة التعديل', 'danger')
        return redirect(url_for('suppliers_product_bp.list_supplier_products'))


@suppliers_product_bp.route('/api/products/update/<path:qid>', methods=['PUT', 'POST'], endpoint='api_update_product')
@login_required
def api_update_product(qid):
    """استقبال وعرض بيانات التعديل المُرسلة عبر FormData من الواجهة"""
    try:
        title = request.form.get('title')
        price = request.form.get('price')
        quantity = request.form.get('quantity')
        sku = request.form.get('sku')
        weight = request.form.get('weight')
        status = request.form.get('status')
        description = request.form.get('description')
        meta_title = request.form.get('meta_title')
        meta_description = request.form.get('meta_description')
        
        image_file = request.files.get('image')

        payload = {
            'title': title,
            'price': price,
            'quantity': quantity,
            'sku': sku,
            'weight': weight,
            'status': status,
            'description': description,
            'meta_title': meta_title,
            'meta_description': meta_description
        }

        # يمكنك ربط دالة التحديث الفعلية هنا عبر الـ services
        # services.products.update_product(qid, payload, image_file)

        return jsonify({
            'success': True,
            'message': 'تم تحديث بيانات المنتج بنجاح'
        })

    except Exception as e:
        current_app.logger.error(f"خطأ أثناء تحديث المنتج {qid}: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': 'حدث خطأ داخلي أثناء حفظ التغييرات'
        }), 500
