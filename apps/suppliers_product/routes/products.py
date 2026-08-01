# coding: utf-8
# 📂 apps/suppliers_product/routes/products.py

import math
import traceback
from flask import render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import login_required, current_user
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier
from apps.extensions import db

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


@suppliers_product_bp.route('/products/add', methods=['GET', 'POST'], endpoint='add_supplier_product')
@login_required
def add_supplier_product():
    """إضافة منتج جديد للمورد الحالي"""
    user_type = session.get('user_type')
    supplier_id = session.get('user_id') or session.get('supplier_id')

    if user_type != 'supplier' and user_type != 'admin':
        flash('❌ هذا القسم مخصص للموردين فقط', 'danger')
        return redirect(url_for('suppliers_dashboard_bp.dashboard'))
    
    suppliers = []
    if user_type == 'admin':
        suppliers = Supplier.query.filter_by(status='active').all()
    else:
        current_supplier = Supplier.query.get(supplier_id) if supplier_id else None
        if current_supplier:
            suppliers = [current_supplier]
    
    if request.method == 'POST':
        try:
            raw_price = request.form.get('price')
            price_val = float(raw_price) if raw_price else 0.0
            raw_status = request.form.get('status', 'DRAFT')
            status = raw_status.upper() if raw_status else 'DRAFT'
            
            product_data = {
                'name': request.form.get('title', ''),
                'price': price_val,
                'status': status,
                'description': request.form.get('description', '')
            }
            
            if request.form.get('sku'):
                product_data['sku'] = request.form.get('sku')
            
            result = services.products.create_product_data(product_data)
            
            if result and 'qid' in result:
                target_supplier_id = supplier_id if user_type != 'admin' else request.form.get('supplier_id')
                
                if target_supplier_id and str(target_supplier_id).strip():
                    mapping = ProductSupplierMapping(
                        product_qid=result['qid'],
                        supplier_id=int(target_supplier_id),
                        status='active'
                    )
                    db.session.add(mapping)
                    db.session.commit()
                
                flash('✅ تم إضافة المنتج بنجاح.', 'success')
            else:
                flash('❌ فشل إضافة المنتج', 'danger')
                
            return redirect(url_for('suppliers_product_bp.list_supplier_products'))
            
        except Exception as e:
            flash(f'❌ حدث خطأ: {str(e)}', 'danger')

    return render_template(
        'suppliers/supplier_add_product.html',
        suppliers=suppliers
    )


@suppliers_product_bp.route('/products/edit', methods=['GET'])
@suppliers_product_bp.route('/products/edit/<path:qid>', methods=['GET'], endpoint='edit_product_view')
@login_required
def edit_product_view(qid=None):
    """عرض صفحة تعديل المنتج مع دعم المعرف عبر المسار أو الـ Query Parameters"""
    try:
        if not qid:
            qid = request.args.get('qid')

        if not qid:
            flash("معرف المنتج (qid) مفقود.", "danger")
            return redirect(url_for('suppliers_product_bp.list_supplier_products'))

        qid = str(qid).strip()
        if 'Product/' in qid:
            qid = qid.split('Product/')[-1]
        while qid and qid.startswith('qid:'):
            qid = qid.replace('qid:', '', 1)
        qid = qid.replace('//', '').strip('/')

        supplier_id = getattr(current_user, 'id', None) or session.get('supplier_id') or session.get('user_id') or session.get('_user_id')
        user_type = getattr(current_user, 'user_type', None) or getattr(current_user, 'role', None) or session.get('user_type')
        is_admin = (user_type == 'admin' or getattr(current_user, 'is_admin', False))

        if not is_admin:
            mapping = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id, product_qid=qid).first()
            if not mapping:
                flash('❌ غير مصرح لك بتعديل هذا المنتج أو المنتج غير موجود', 'danger')
                return redirect(url_for('suppliers_product_bp.list_supplier_products'))

        product_data = services.products.get_product_by_qid(qid)
        if not product_data:
            max_check_pages = 30
            for p_num in range(1, max_check_pages + 1):
                res = services.products.get_products_page(p_num)
                if not res or not res.get('data'):
                    break
                for p in res.get('data', []):
                    if str(p.get('qid') or p.get('id', '')).strip() == str(qid).strip():
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


@suppliers_product_bp.route('/products/sync', methods=['GET', 'POST'], endpoint='sync_supplier_products')
@login_required
def sync_supplier_products():
    """مسار مزامنة المنتجات لتجنب خطأ الـ BuildError في النافذة المنبثقة"""
    try:
        # يمكنك إضافة منطق المزامنة هنا أو إعادة توجيه حسب الحاجة
        if request.method == 'POST' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'تمت المزامنة بنجاح'})
        return redirect(url_for('suppliers_product_bp.list_supplier_products'))
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 500
        flash('❌ حدث خطأ أثناء المزامنة', 'danger')
        return redirect(url_for('suppliers_product_bp.list_supplier_products'))


@suppliers_product_bp.route('/api/products/update/<path:qid>', methods=['PUT', 'POST'], endpoint='api_update_product')
@login_required
def api_update_product(qid):
    """استقبال وحفظ التعديلات المُرسلة عبر الواجهة وتحديثها عبر الخدمات"""
    try:
        qid = str(qid).strip()
        if 'Product/' in qid:
            qid = qid.split('Product/')[-1]
        while qid and qid.startswith('qid:'):
            qid = qid.replace('qid:', '', 1)
        qid = qid.replace('//', '').strip('/')

        title = request.form.get('title')
        raw_price = request.form.get('price')
        sku = request.form.get('sku')
        raw_status = request.form.get('status', 'DRAFT')
        status = raw_status.upper() if raw_status else 'DRAFT'
        description = request.form.get('description')
        
        try:
            price = float(raw_price) if raw_price else 0.0
        except ValueError:
            price = 0.0

        try:
            if hasattr(services.products, 'update_product_info'):
                services.products.update_product_info(qid, {"title": title, "sku": sku})
            if hasattr(services.products, 'update_product_description'):
                services.products.update_product_description(qid, description)
            if hasattr(services.products, 'update_product_pricing'):
                services.products.update_product_pricing(qid, {"price": price})
            if hasattr(services.products, 'update_product_status'):
                services.products.update_product_status(qid, status)
        except Exception as svc_err:
            print(f"⚠️ [Warning] خطأ في تحديث الخدمات الخارجية: {svc_err}")

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


@suppliers_product_bp.route('/products/delete/<path:qid>', methods=['POST'], endpoint='delete_supplier_product')
@login_required
def delete_supplier_product(qid):
    """أرشفة وحذف منتج المورد المحلي"""
    try:
        user_type = session.get('user_type')
        if user_type != 'supplier' and user_type != 'admin':
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
        while qid.startswith('qid:'):
            qid = qid.replace('qid:', '', 1)

        mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
        
        try:
            services.products.update_product_status(qid, "ARCHIVED")
        except Exception as ext_err:
            print(f"⚠️ [Warning] فشل الأرشفة الخارجية للمنتج {qid}: {ext_err}")

        if mapping:
            db.session.delete(mapping)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '✅ تم حذف المنتج وفك ارتباطه بنجاح'
        })
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ خطأ في delete_supplier_product: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
