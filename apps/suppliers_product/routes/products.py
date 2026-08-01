# coding: utf-8
# 📂 apps/suppliers_product/routes/products.py

import traceback
from flask import render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import login_required, current_user
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.extensions import db
from datetime import datetime


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


def _sync_products_in_background(supplier_id):
    try:
        mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
        if not mappings: return
        
        updated_count = 0
        for mapping in mappings:
            qid = mapping.product_qid
            product_data = services.products.get_product_by_qid(qid)
            if product_data:
                mapping.updated_at = datetime.utcnow()
                updated_count += 1
        
        db.session.commit()
        print(f"✅ [Sync Background] تم تحديث {updated_count} منتج للمورد {supplier_id}")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ [Sync Background Error] {e}")


@suppliers_product_bp.route('/products', methods=['GET'], endpoint='list_supplier_products')
@login_required
def manage_supplier_products_view():
    try:
        supplier_id = getattr(current_user, 'id', None) or session.get('supplier_id') or session.get('user_id')
        user_type = getattr(current_user, 'user_type', None) or session.get('user_type')
        is_admin = (user_type == 'admin' or getattr(current_user, 'is_admin', False))

        if user_type not in ('supplier', 'admin') and not is_admin:
            flash('❌ غير مصرح لك بالدخول', 'danger')
            return redirect(url_for('suppliers_dashboard_bp.dashboard'))

        # ============================================================
        # 1. المزامنة الخلفية
        # ============================================================
        last_sync_key = f'_last_sync_{supplier_id}'
        if not is_admin and supplier_id:
            last_sync_time = session.get(last_sync_key)
            if last_sync_time and hasattr(last_sync_time, 'tzinfo') and last_sync_time.tzinfo is not None:
                last_sync_time = last_sync_time.replace(tzinfo=None)
            if not last_sync_time or (datetime.utcnow() - last_sync_time).seconds > 600:
                _sync_products_in_background(supplier_id)
                session[last_sync_key] = datetime.utcnow()

        # ============================================================
        # 2. جلب المنتجات
        # ============================================================
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('limit', 10, type=int)
        per_page = max(1, min(per_page, 50))
        is_ajax = request.args.get('ajax', '0') == '1' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        query = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id)
        status_filter = request.args.get('status', '').strip()
        if status_filter:
            query = query.filter_by(status=status_filter)

        search_term = request.args.get('search', '').strip().lower()
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        mappings = pagination.items

        # ============================================================
        # 3. جلب تفاصيل المنتجات مع الفلاتر
        # ============================================================
        products_data = []
        for mapping in mappings:
            qid = mapping.product_qid
            product = services.products.get_product_by_qid(qid)
            
            # ✅ تجاهل المنتجات التي لا يوجد لها بيانات
            if not product:
                continue

            if search_term:
                title = str(product.get('title', '')).lower()
                sku = str(product.get('sku', '')).lower()
                if search_term not in title and search_term not in sku:
                    continue

            try:
                price_val = float(product.get('price') or product.get('sale_price') or product.get('regular_price') or 0)
                if min_price and price_val < float(min_price):
                    continue
                if max_price and price_val > float(max_price):
                    continue
            except (ValueError, TypeError):
                pass

            products_data.append({'mapping': mapping, 'product': product})

        # ============================================================
        # 4. تجهيز بيانات الترقيم
        # ============================================================
        total_filtered = len(products_data)
        total_pages = (total_filtered + per_page - 1) // per_page if total_filtered > 0 else 1

        pagination_info = {
            'current_page': page,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_num': page - 1 if page > 1 else None,
            'next_num': page + 1 if page < total_pages else None,
            'per_page': per_page,
            'total_items': total_filtered
        }

        if is_ajax:
            return jsonify({
                'success': True,
                'html': render_template('suppliers/includes/_product_grid.html', products=products_data, get_status_text=get_status_text, format_price=format_price),
                'pagination_html': render_template('suppliers/includes/_pagination.html', pagination=pagination_info),
                'total_items': pagination_info['total_items']
            })

        return render_template('suppliers/suppliers_product.html', products=products_data, pagination=pagination_info, get_status_text=get_status_text, format_price=format_price)

    except Exception as e:
        current_app.logger.error(f"خطأ غير متوقع: {traceback.format_exc()}")
        flash('❌ حدث خطأ غير متوقع أثناء تحميل المنتجات', 'danger')
        is_ajax = request.args.get('ajax', '0') == '1' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            return jsonify({'success': False, 'message': 'حدث خطأ أثناء تحميل المنتجات'}), 500
        return render_template('suppliers/suppliers_product.html', products=[], pagination={'total_pages': 0, 'total_items': 0, 'current_page': 1}, get_status_text=get_status_text, format_price=format_price)


# ============================================================================================
# 🛠️ صفحة تعديل المنتج (الحل النهائي: تقبل GET و POST معاً)
# ============================================================================================
@suppliers_product_bp.route('/products/edit/<string:product_qid>', methods=['GET', 'POST'], endpoint='edit_supplier_product')
@login_required
def edit_supplier_product(product_qid):
    try:
        supplier_id = getattr(current_user, 'id', None) or session.get('supplier_id') or session.get('user_id')
        
        # 1. التحقق من وجود العلاقة
        mapping = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id, product_qid=product_qid).first()
        if not mapping:
            flash('⚠️ لا تملك الصلاحية لتعديل هذا المنتج.', 'danger')
            return redirect(url_for('suppliers_product_bp.list_supplier_products'))

        # 2. جلب المنتج
        product = services.products.get_product_by_qid(product_qid)
        if not product:
            flash('❌ هذا المنتج غير موجود أو تم حذفه.', 'danger')
            db.session.delete(mapping)
            db.session.commit()
            return redirect(url_for('suppliers_product_bp.list_supplier_products'))

        # 3. معالجة الحفظ (POST)
        if request.method == 'POST':
            price = request.form.get('price')
            quantity = request.form.get('quantity')
            status = request.form.get('status')

            if price is not None and price != '':
                mapping.price = float(price)
            if quantity is not None and quantity != '':
                mapping.quantity = int(quantity)
            if status:
                mapping.status = status

            mapping.updated_at = datetime.utcnow()
            db.session.commit()

            flash('✅ تم حفظ وتعديل المنتج بنجاح!', 'success')
            return redirect(url_for('suppliers_product_bp.list_supplier_products'))

        # 4. عرض صفحة التعديل (GET)
        return render_template('suppliers/edit_product.html', mapping=mapping, product=product)

    except Exception as e:
        current_app.logger.error(f"خطأ في صفحة التعديل: {traceback.format_exc()}")
        flash('❌ حدث خطأ غير متوقع أثناء تحميل الصفحة', 'danger')
        return redirect(url_for('suppliers_product_bp.list_supplier_products'))


# ============================================================================================
# 🆕 إضافة صفحة منتج جديد (احتياطية، لمنع 404 مستقبلاً)
# ============================================================================================
@suppliers_product_bp.route('/products/add', methods=['GET'], endpoint='add_supplier_product')
@login_required
def add_supplier_product():
    flash('⚠️ صفحة إضافة منتج جديد قيد التطوير حالياً.', 'warning')
    return redirect(url_for('suppliers_product_bp.list_supplier_products'))
