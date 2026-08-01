# coding: utf-8
# apps/suppliers_product/routes/crud.py

from flask import render_template, request, jsonify, redirect, url_for, flash, session, current_app
from flask_login import login_required, current_user
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier
from apps.extensions import db
from datetime import datetime
import traceback


# =============================================
# دالة مساعدة لاستخراج المعرف الخام من صيغة QID
# =============================================
def _extract_raw_id(qid):
    """تستخرج المعرف الخام (مثل 01KNSQ2Z4NH8VDJ8KVR0EXEDRC) من صيغ مختلفة"""
    if not qid:
        return None
    qid_str = str(qid).strip()
    if 'qid://' in qid_str or 'qumra/' in qid_str:
        parts = qid_str.split('/')
        return parts[-1] if parts else qid_str
    if qid_str.startswith('qid:'):
        return qid_str[4:]
    return qid_str


# =============================================
# دالة مساعدة لتوحيد رسائل الأخطاء
# =============================================
def _log_error(error, context='', log_level='error'):
    """تسجيل الأخطاء بشكل موحد"""
    msg = f"{context} - {str(error)}" if context else str(error)
    if log_level == 'error':
        current_app.logger.error(msg)
    elif log_level == 'warning':
        current_app.logger.warning(msg)
    else:
        current_app.logger.info(msg)
    return msg


def _json_error(message, status_code=400, details=None):
    """إرجاع رد خطأ بتنسيق JSON موحد"""
    response = {'success': False, 'message': message}
    if details:
        response['details'] = details
    return jsonify(response), status_code


# ============================================================
# 1. إضافة منتج جديد
# ============================================================
@suppliers_product_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_supplier_product():
    try:
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
                    flash('❌ فشل إضافة المنتج في النظام الخارجي.', 'danger')
                return redirect(url_for('suppliers_product_bp.list_supplier_products'))
                
            except ValueError as ve:
                db.session.rollback()
                flash(f'❌ خطأ في صيغة البيانات: {str(ve)}', 'danger')
                _log_error(ve, 'add_supplier_product - ValueError')
                
            except Exception as e:
                db.session.rollback()
                flash(f'❌ حدث خطأ أثناء إضافة المنتج: {str(e)}', 'danger')
                _log_error(e, 'add_supplier_product', 'error')

        return render_template('suppliers/supplier_add_product.html', suppliers=suppliers)
        
    except Exception as e:
        _log_error(e, 'add_supplier_product - غير متوقع', 'error')
        flash('❌ حدث خطأ غير متوقع في إضافة المنتج', 'danger')
        return redirect(url_for('suppliers_product_bp.list_supplier_products'))


# ============================================================
# 2. تعديل المنتج (عرض صفحة التعديل)
# ============================================================
@suppliers_product_bp.route('/products/edit', methods=['GET'])
@suppliers_product_bp.route('/products/edit/<path:qid>', methods=['GET'])
@login_required
def edit_supplier_product(qid=None):
    try:
        # ✅ سجل الـ qid للتصحيح
        current_app.logger.info(f"🔍 [edit_supplier_product] QID المستلم: {qid}")
        
        if not qid:
            qid = request.args.get('qid')
            current_app.logger.info(f"🔍 [edit_supplier_product] QID من query: {qid}")

        user_type = session.get('user_type') or getattr(current_user, 'user_type', None)
        supplier_id = session.get('user_id') or session.get('supplier_id') or getattr(current_user, 'id', None)

        if user_type not in ('supplier', 'admin'):
            flash('❌ هذا القسم مخصص للموردين فقط', 'danger')
            return redirect(url_for('suppliers_dashboard_bp.dashboard'))
        
        if not qid:
            flash("معرف المنتج (qid) مفقود.", "danger")
            return redirect(url_for('suppliers_product_bp.list_supplier_products'))
        
        # استخراج المعرف الخام (يُستخدم فقط للـ API)
        raw_qid_for_api = _extract_raw_id(qid)
        current_app.logger.info(f"🔍 [edit_supplier_product] raw_qid_for_api: {raw_qid_for_api}")
        
        if not raw_qid_for_api:
            flash("❌ معرف المنتج غير صالح", "danger")
            return redirect(url_for('suppliers_product_bp.list_supplier_products'))
        
        # ============================================================
        # المحاولة 1: جلب المنتج باستخدام المعرف الخام
        # ============================================================
        product = None
        try:
            product = services.products.get_product_by_qid(raw_qid_for_api)
            if product:
                current_app.logger.info(f"✅ [edit_supplier_product] تم جلب المنتج بالمعرف الخام: {raw_qid_for_api}")
        except Exception as api_err:
            _log_error(api_err, f'get_product_by_qid(raw={raw_qid_for_api})', 'warning')
        
        # ============================================================
        # المحاولة 2: جلب المنتج باستخدام المعرف الأصلي (الكامل)
        # ============================================================
        if not product:
            try:
                current_app.logger.info(f"⚠️ [edit_supplier_product] المعرف الخام فشل، نحاول بالكامل: {qid}")
                product = services.products.get_product_by_qid(qid)
                if product:
                    current_app.logger.info(f"✅ [edit_supplier_product] تم جلب المنتج بالمعرف الكامل: {qid}")
            except Exception as api_err:
                _log_error(api_err, f'get_product_by_qid(full={qid})', 'warning')
        
        # ============================================================
        # المحاولة 3: البحث عبر صفحات الـ API (حل احتياطي)
        # ============================================================
        if not product:
            current_app.logger.info("🔄 [edit_supplier_product] المعرفان فشلا، نبحث عبر صفحات الـ API...")
            max_pages = 30
            for page_num in range(1, max_pages + 1):
                try:
                    result = services.products.get_products_page(page_num)
                    if not result or not result.get('data'):
                        break
                    for p in result.get('data', []):
                        p_qid = str(p.get('qid') or p.get('id', '')).strip()
                        # نبحث باستخدام المعرف الخام أو الكامل أو أي جزء منهما
                        if (raw_qid_for_api in p_qid or qid in p_qid or 
                            p_qid == raw_qid_for_api or p_qid == qid):
                            product = p
                            current_app.logger.info(f"✅ [edit_supplier_product] وجدنا المنتج في الصفحة {page_num}: {product.get('title')}")
                            break
                    if product:
                        break
                except Exception as page_err:
                    current_app.logger.warning(f"⚠️ [edit_supplier_product] خطأ في الصفحة {page_num}: {page_err}")
                    continue
        
        # ============================================================
        # إذا لم نجد المنتج بعد كل المحاولات
        # ============================================================
        if not product:
            flash("❌ لم يتم العثور على المنتج في النظام الخارجي", "danger")
            return redirect(url_for('suppliers_product_bp.list_supplier_products'))

        # ============================================================
        # البحث في جدول الربط (نستخدم المعرف الأصلي للتخزين)
        # ============================================================
        mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
        if not mapping and raw_qid_for_api:
            mapping = ProductSupplierMapping.query.filter_by(product_qid=raw_qid_for_api).first()

        # إنشاء ربط تلقائي للمورد (إذا لم يكن موجوداً)
        if user_type != 'admin' and not mapping and supplier_id:
            try:
                mapping = ProductSupplierMapping(
                    product_qid=qid,
                    supplier_id=int(supplier_id),
                    status='active'
                )
                db.session.add(mapping)
                db.session.commit()
                current_app.logger.info(f"✅ [edit_supplier_product] تم إنشاء ربط تلقائي للمورد {supplier_id}")
            except Exception as map_err:
                db.session.rollback()
                _log_error(map_err, f'إنشاء ربط تلقائي للمورد {supplier_id}', 'warning')
                flash("⚠️ تم جلب المنتج ولكن حدث خطأ في ربطه بحسابك.", "warning")

        # إذا كان الربط موجوداً لمورد آخر والمستخدم ليس أدمن، نمنع التعديل
        if mapping and user_type != 'admin' and str(mapping.supplier_id) != str(supplier_id):
            flash("❌ هذا المنتج مرتبط بمورد آخر، لا يمكنك تعديله.", "danger")
            return redirect(url_for('suppliers_product_bp.list_supplier_products'))

        # ============================================================
        # جلب الخيارات (variants/options)
        # ============================================================
        raw_options = []
        try:
            if isinstance(product, dict):
                raw_options = product.get('options', [])
            else:
                raw_options = getattr(product, 'options', [])
        except Exception as opt_err:
            _log_error(opt_err, f'جلب options للمنتج {qid}', 'warning')

        if not raw_options and hasattr(services, 'variants'):
            try:
                options_data = services.variants.get_all_options_for_product(qid)
                if isinstance(options_data, list):
                    raw_options = options_data
                elif isinstance(options_data, dict):
                    raw_options = [options_data]
            except Exception as e:
                _log_error(e, f'get_all_options_for_product({qid})', 'warning')

        cleaned_options = []
        if isinstance(raw_options, list):
            for opt in raw_options:
                if isinstance(opt, dict):
                    vals = opt.get('values', [])
                    if not isinstance(vals, list):
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

        # ============================================================
        # تجهيز القالب
        # ============================================================
        suppliers = []
        if user_type == 'admin':
            suppliers = Supplier.query.filter_by(status='active').all()
        else:
            curr_sup = Supplier.query.get(supplier_id) if supplier_id else None
            if curr_sup:
                suppliers = [curr_sup]

        assigned_supplier_id = mapping.supplier_id if mapping else None

        all_collections = []
        try:
            if hasattr(services, 'collections') and hasattr(services.collections, 'get_all_collections'):
                all_collections = services.collections.get_all_collections()
        except Exception as e:
            _log_error(e, 'get_all_collections', 'warning')

        return render_template(
            'suppliers/supplier_edit_product.html',
            product=product,
            suppliers=suppliers,
            assigned_supplier_id=assigned_supplier_id,
            all_collections=all_collections
        )

    except Exception as e:
        _log_error(e, 'edit_supplier_product', 'error')
        flash('❌ حدث خطأ غير متوقع أثناء تحميل صفحة التعديل', 'danger')
        return redirect(url_for('suppliers_product_bp.list_supplier_products'))


# ============================================================
# 3. حفظ التعديلات (sync)
# ============================================================
@suppliers_product_bp.route('/products/save-sync', methods=['POST'])
@login_required
def save_sync_supplier_product():
    try:
        user_type = session.get('user_type') or getattr(current_user, 'user_type', None)
        supplier_id = session.get('user_id') or session.get('supplier_id') or getattr(current_user, 'id', None)

        if user_type not in ('supplier', 'admin'):
            return _json_error('غير مصرح لك بهذه العملية', 403)

        qid = request.form.get('qid')
        if not qid:
            return _json_error('معرف المنتج (qid) مفقود.', 400)

        raw_qid_for_api = _extract_raw_id(qid)
        if not raw_qid_for_api:
            return _json_error('معرف المنتج غير صالح', 400)

        # تحديث الربط
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
                    _log_error(map_err, 'save_sync - إنشاء ربط', 'warning')
                    return _json_error('فشل إنشاء ربط المنتج', 500)
            elif mapping and str(mapping.supplier_id) != str(supplier_id):
                try:
                    mapping.supplier_id = int(supplier_id)
                    db.session.commit()
                except Exception as map_err:
                    db.session.rollback()
                    _log_error(map_err, 'save_sync - تحديث الربط', 'warning')
                    return _json_error('فشل تحديث ربط المنتج', 500)

        # قراءة البيانات من النموذج
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
            compare_price = request.form.get('compare_price')
            compare_price = float(compare_price) if compare_price else None
        except ValueError:
            compare_price = None

        collection_ids = request.form.getlist('collection_ids')

        # تحديث البيانات في الـ API باستخدام المعرف الخام
        errors = []
        try:
            if hasattr(services.products, 'update_product_info'):
                services.products.update_product_info(raw_qid_for_api, {"title": title, "sku": sku})
        except Exception as e:
            errors.append(f"معلومات المنتج: {str(e)}")
            _log_error(e, 'update_product_info', 'warning')

        try:
            if hasattr(services.products, 'update_product_description'):
                services.products.update_product_description(raw_qid_for_api, description)
        except Exception as e:
            errors.append(f"الوصف: {str(e)}")
            _log_error(e, 'update_product_description', 'warning')

        try:
            if hasattr(services.products, 'update_product_pricing'):
                pricing_data = {"price": price}
                if compare_price is not None:
                    pricing_data["compareAtPrice"] = compare_price
                services.products.update_product_pricing(raw_qid_for_api, pricing_data)
        except Exception as e:
            errors.append(f"التسعير: {str(e)}")
            _log_error(e, 'update_product_pricing', 'warning')

        if collection_ids:
            try:
                if hasattr(services.products, 'update_product_collection'):
                    services.products.update_product_collection(raw_qid_for_api, collection_ids)
            except Exception as e:
                errors.append(f"المجموعات: {str(e)}")
                _log_error(e, 'update_product_collection', 'warning')

        try:
            if hasattr(services.products, 'update_product_status'):
                services.products.update_product_status(raw_qid_for_api, status)
        except Exception as e:
            errors.append(f"الحالة: {str(e)}")
            _log_error(e, 'update_product_status', 'warning')

        if errors:
            return jsonify({
                "status": "warning",
                "message": "تم الحفظ مع بعض التحذيرات",
                "errors": errors
            }), 207

        return jsonify({"status": "success", "message": "تم حفظ وتحديث المنتج بنجاح!"})

    except Exception as e:
        _log_error(e, 'save_sync_supplier_product', 'error')
        return _json_error(f'حدث خطأ داخلي: {str(e)}', 500)


# ============================================================
# 4. حذف المنتج (أرشفة)
# ============================================================
@suppliers_product_bp.route('/products/delete/<path:qid>', methods=['POST'])
@login_required
def delete_supplier_product(qid):
    try:
        user_type = session.get('user_type') or getattr(current_user, 'user_type', None)
        supplier_id = session.get('user_id') or session.get('supplier_id') or getattr(current_user, 'id', None)

        if user_type not in ('supplier', 'admin'):
            return _json_error('غير مصرح لك بهذه العملية', 403)

        raw_qid_for_api = _extract_raw_id(qid)
        if not raw_qid_for_api:
            return _json_error('معرف المنتج غير صالح', 400)

        mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
        if not mapping:
            return _json_error('المنتج غير موجود في قائمتك', 404)

        # أرشفة المنتج في الـ API باستخدام المعرف الخام
        try:
            services.products.update_product_status(raw_qid_for_api, "ARCHIVED")
        except Exception as ext_err:
            _log_error(ext_err, f'update_product_status({qid})', 'warning')
            # نستمر في الحذف المحلي حتى لو فشلت الأرشفة الخارجية

        # حذف الربط من قاعدة البيانات
        try:
            db.session.delete(mapping)
            db.session.commit()
        except Exception as db_err:
            db.session.rollback()
            _log_error(db_err, f'delete mapping {qid}', 'error')
            return _json_error('فشل حذف المنتج من قاعدة البيانات', 500)

        return jsonify({'success': True, 'message': '✅ تم حذف المنتج وفك ارتباطه بنجاح'})

    except Exception as e:
        db.session.rollback()
        _log_error(e, f'delete_supplier_product({qid})', 'error')
        return _json_error(f'حدث خطأ داخلي: {str(e)}', 500)


# ============================================================
# 5. المزامنة الجماعية (للاستخدام المستقبلي)
# ============================================================
@suppliers_product_bp.route('/products/sync-batch', methods=['POST'])
@login_required
def sync_batch_products():
    try:
        data = request.get_json()
        if not data:
            return _json_error('البيانات غير صالحة', 400)

        page = data.get('page', 1)
        if not isinstance(page, int) or page < 1:
            return _json_error('رقم الصفحة غير صالح', 400)

        user_type = getattr(current_user, 'user_type', None) or session.get('user_type')
        is_admin = (user_type == 'admin' or getattr(current_user, 'is_admin', False))
        supplier_id = getattr(current_user, 'id', None) or session.get('user_id') or session.get('supplier_id')

        if not is_admin and not supplier_id:
            return _json_error('معرف المورد غير موجود، يرجى تسجيل الدخول كمورد', 400)

        # جلب المنتجات من الـ API
        try:
            result = services.products.get_products_page(page)
        except Exception as api_err:
            _log_error(api_err, f'sync_batch - get_products_page({page})', 'error')
            return _json_error('فشل جلب المنتجات من النظام الخارجي', 500)

        if not result or not result.get('data'):
            return _json_error('لا توجد منتجات في هذه الصفحة', 404)

        products_list = result.get('data', [])
        synced_count = 0
        updated_count = 0

        if is_admin:
            synced_count = len(products_list)
        else:
            try:
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
                db.session.commit()
            except Exception as db_err:
                db.session.rollback()
                _log_error(db_err, 'sync_batch - تحديث قاعدة البيانات', 'error')
                return _json_error('فشل تحديث قاعدة البيانات', 500)

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
        _log_error(e, 'sync_batch_products', 'error')
        return _json_error(f'حدث خطأ داخلي: {str(e)}', 500)
