# coding: utf-8
# apps/suppliers_product/routes/crud.py

from flask import render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required, current_user
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier
from apps.extensions import db
from datetime import datetime


# =============================================
# دالة مساعدة لاستخراج المعرف الخام من صيغة QID
# =============================================
def _extract_raw_id(qid):
    if not qid:
        return qid
    qid_str = str(qid)
    if 'qid://' in qid_str or 'qumra/' in qid_str:
        parts = qid_str.split('/')
        return parts[-1] if parts else qid_str
    if qid_str.startswith('qid:'):
        return qid_str[4:]
    return qid_str


@suppliers_product_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_supplier_product():
    user_type = session.get('user_type') or getattr(current_user, 'user_type', None)
    supplier_id = session.get('user_id') or session.get('supplier_id') or getattr(current_user, 'id', None)

    if user_type not in ('supplier', 'admin'):
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

    return render_template('suppliers/supplier_add_product.html', suppliers=suppliers)


@suppliers_product_bp.route('/products/edit', methods=['GET'])
@suppliers_product_bp.route('/products/edit/<path:qid>', methods=['GET'])
@login_required
def edit_supplier_product(qid=None):
    if not qid:
        qid = request.args.get('qid')

    user_type = session.get('user_type') or getattr(current_user, 'user_type', None)
    supplier_id = session.get('user_id') or session.get('supplier_id') or getattr(current_user, 'id', None)

    if user_type not in ('supplier', 'admin'):
        flash('❌ هذا القسم مخصص للموردين فقط', 'danger')
        return redirect(url_for('suppliers_dashboard_bp.dashboard'))
    
    if not qid:
        flash("معرف المنتج (qid) مفقود.", "danger")
        return redirect(url_for('suppliers_product_bp.list_supplier_products'))
    
    raw_qid_for_api = _extract_raw_id(qid)
    product = services.products.get_product_by_qid(raw_qid_for_api)
    if not product:
        product = services.products.get_product_by_qid(qid)

    if not product:
        flash("❌ لم يتم العثور على المنتج", "danger")
        return redirect(url_for('suppliers_product_bp.list_supplier_products'))

    mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()

    if user_type != 'admin':
        if not mapping and supplier_id:
            try:
                mapping = ProductSupplierMapping(
                    product_qid=qid,
                    supplier_id=int(supplier_id),
                    status='active'
                )
                db.session.add(mapping)
                db.session.commit()
            except Exception as map_err:
                db.session.rollback()
                print(f"⚠️ [Warning] تعذر إنشاء ربط تلقائي: {map_err}")
        
        if mapping and str(mapping.supplier_id) != str(supplier_id):
            try:
                mapping.supplier_id = int(supplier_id)
                db.session.commit()
            except Exception as e:
                db.session.rollback()

    # جلب الخيارات (variants/options)
    raw_options = []
    if isinstance(product, dict):
        raw_options = product.get('options', [])
    else:
        raw_options = getattr(product, 'options', [])

    if not raw_options and hasattr(services, 'variants'):
        try:
            options_data = services.variants.get_all_options_for_product(qid)
            if isinstance(options_data, list):
                raw_options = options_data
            elif isinstance(options_data, dict):
                raw_options = [options_data]
        except Exception as e:
            print(f"⚠️ [Edit Supplier Product] تعذر جلب الخيارات: {e}")

    cleaned_options = []
    if isinstance(raw_options, list):
        for opt in raw_options:
            if isinstance(opt, dict):
                vals = opt.get('values', [])
                if callable(vals) or not isinstance(vals, list):
                    vals = []
                cleaned_options.append({
                    "qid": opt.get('qid'),
                    "name": opt.get('name'),
                    "type": opt.get('type'),
                    "values": vals
                })

    if isinstance(product, dict):
        product['options'] = cleaned_options
    else:
        setattr(product, 'options', cleaned_options)

    suppliers = []
    if user_type == 'admin':
        suppliers = Supplier.query.filter_by(status='active').all()
    else:
        curr_sup = Supplier.query.get(supplier_id) if supplier_id else None
        if curr_sup:
            suppliers = [curr_sup]

    assigned_supplier_id = mapping.supplier_id if mapping else None

    try:
        all_collections = services.collections.get_all_collections() if hasattr(services, 'collections') else []
    except Exception as e:
        print(f"❌ [DEBUG] Error loading collections: {e}")
        all_collections = []

    return render_template(
        'suppliers/supplier_edit_product.html',
        product=product,
        suppliers=suppliers,
        assigned_supplier_id=assigned_supplier_id,
        all_collections=all_collections
    )


@suppliers_product_bp.route('/products/save-sync', methods=['POST'])
@login_required
def save_sync_supplier_product():
    user_type = session.get('user_type') or getattr(current_user, 'user_type', None)
    supplier_id = session.get('user_id') or session.get('supplier_id') or getattr(current_user, 'id', None)

    if user_type not in ('supplier', 'admin'):
        return jsonify({"status": "error", "message": "غير مصرح"}), 403
    
    try:
        qid = request.form.get('qid')
        if not qid:
            return jsonify({"status": "error", "message": "معرف المنتج (qid) مفقود."}), 400

        raw_qid_for_api = _extract_raw_id(qid)

        mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
        if user_type != 'admin':
            if not mapping:
                try:
                    mapping = ProductSupplierMapping(
                        product_qid=qid,
                        supplier_id=int(supplier_id),
                        status='active'
                    )
                    db.session.add(mapping)
                    db.session.commit()
                except:
                    db.session.rollback()
            elif str(mapping.supplier_id) != str(supplier_id):
                mapping.supplier_id = int(supplier_id)
                db.session.commit()

        title = request.form.get('title', '')
        description = request.form.get('description', '')
        raw_status = request.form.get('status', 'DRAFT')
        status = raw_status.upper() if raw_status else 'DRAFT'
        sku = request.form.get('sku', '')
        
        try:
            price = float(request.form.get('price', 0))
        except ValueError:
            price = 0.0
        
        try:
            compare_price = float(request.form.get('compare_price', 0)) if request.form.get('compare_price') else None
        except ValueError:
            compare_price = None

        collection_ids = request.form.getlist('collection_ids')

        try:
            if hasattr(services.products, 'update_product_info'):
                services.products.update_product_info(raw_qid_for_api, {"title": title, "sku": sku})
        except Exception as e:
            print(f"⚠️ [Warning] فشل تحديث معلومات المنتج: {e}")

        try:
            if hasattr(services.products, 'update_product_description'):
                services.products.update_product_description(raw_qid_for_api, description)
        except Exception as e:
            print(f"⚠️ [Warning] فشل تحديث وصف المنتج: {e}")

        try:
            if hasattr(services.products, 'update_product_pricing'):
                pricing_data = {"price": price}
                if compare_price is not None:
                    pricing_data["compareAtPrice"] = compare_price
                services.products.update_product_pricing(raw_qid_for_api, pricing_data)
        except Exception as e:
            print(f"⚠️ [Warning] فشل تحديث التسعير: {e}")

        if collection_ids:
            try:
                if hasattr(services.products, 'update_product_collection'):
                    services.products.update_product_collection(raw_qid_for_api, collection_ids)
            except Exception as e:
                print(f"⚠️ [Warning] فشل تحديث مجموعات المنتج: {e}")

        try:
            if hasattr(services.products, 'update_product_status'):
                services.products.update_product_status(raw_qid_for_api, status)
        except Exception as e:
            print(f"⚠️ [Warning] حدث خطأ أثناء تحديث الحالة: {e}")

        return jsonify({"status": "success", "message": "تم حفظ وتحديث المنتج بنجاح!"})

    except Exception as e:
        print(f"❌ خطأ غير متوقع في save_sync_supplier_product: {e}")
        return jsonify({"status": "error", "message": f"حدث خطأ: {str(e)}"}), 500


@suppliers_product_bp.route('/products/delete/<path:qid>', methods=['POST'])
@login_required
def delete_supplier_product(qid):
    try:
        user_type = session.get('user_type') or getattr(current_user, 'user_type', None)
        supplier_id = session.get('user_id') or session.get('supplier_id') or getattr(current_user, 'id', None)

        if user_type not in ('supplier', 'admin'):
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
        raw_qid_for_api = _extract_raw_id(qid)
        mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
        
        try:
            services.products.update_product_status(raw_qid_for_api, "ARCHIVED")
        except Exception as ext_err:
            print(f"⚠️ [Warning] فشل الأرشفة الخارجية للمنتج {qid}: {ext_err}")

        if mapping:
            db.session.delete(mapping)
            db.session.commit()
        
        return jsonify({'success': True, 'message': '✅ تم حذف المنتج وفك ارتباطه بنجاح'})
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ خطأ في delete_supplier_product: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# ✅ دالة المزامنة الجماعية (للاستخدام مع _sync_modal.html)
# ============================================================
@suppliers_product_bp.route('/products/sync-batch', methods=['POST'])
@login_required
def sync_batch_products():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'البيانات غير صالحة'}), 400

        page = data.get('page', 1)

        user_type = getattr(current_user, 'user_type', None) or session.get('user_type')
        is_admin = (user_type == 'admin' or getattr(current_user, 'is_admin', False))
        supplier_id = getattr(current_user, 'id', None) or session.get('user_id') or session.get('supplier_id')

        if not is_admin and not supplier_id:
            return jsonify({'success': False, 'message': 'معرف المورد غير موجود، يرجى تسجيل الدخول كمورد'}), 400

        result = services.products.get_products_page(page)
        if not result or not result.get('data'):
            return jsonify({
                'success': False,
                'message': 'لا توجد منتجات في هذه الصفحة'
            }), 404

        products_list = result.get('data', [])
        synced_count = 0
        updated_count = 0

        if is_admin:
            synced_count = len(products_list)
        else:
            for product in products_list:
                qid = product.get('qid')
                if not qid:
                    continue

                mapping = ProductSupplierMapping.query.filter_by(
                    product_qid=qid,
                    supplier_id=int(supplier_id)
                ).first()

                if mapping:
                    mapping.updated_at = datetime.utcnow()
                    updated_count += 1
                else:
                    pass

            db.session.commit()

        pagination = result.get('pagination', {})
        total_pages = pagination.get('totalPages', 1)
        has_next = pagination.get('hasNextPage', False)

        return jsonify({
            'success': True,
            'message': 'تمت المزامنة بنجاح',
            'syncedCount': synced_count,
            'updatedCount': updated_count,
            'total_pages': total_pages,
            'has_next': has_next,
            'next_page': page + 1 if has_next else None,
            'current_page': page,
            'total_items': pagination.get('totalItems', 0)
        })

    except Exception as e:
        db.session.rollback()
        print(f"❌ خطأ في sync_batch_products: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'حدث خطأ داخلي: {str(e)}'
        }), 500
