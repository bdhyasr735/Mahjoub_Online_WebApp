# coding: utf-8
# apps/suppliers_product/routes/crud.py

from flask import render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier
from apps.extensions import db
from datetime import datetime


@suppliers_product_bp.route('/products/add', methods=['GET', 'POST'])
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
                
            return redirect(url_for('suppliers_product_bp.sync_supplier_products'))
            
        except Exception as e:
            flash(f'❌ حدث خطأ: {str(e)}', 'danger')

    return render_template(
        'suppliers/supplier_add_product.html',
        suppliers=suppliers
    )


@suppliers_product_bp.route('/products/edit/<path:qid>', methods=['GET'])
@login_required
def edit_supplier_product(qid):
    """عرض صفحة تعديل المنتج للمورد"""
    user_type = session.get('user_type')
    supplier_id = session.get('user_id') or session.get('supplier_id')

    if user_type != 'supplier' and user_type != 'admin':
        flash('❌ هذا القسم مخصص للموردين فقط', 'danger')
        return redirect(url_for('suppliers_dashboard_bp.dashboard'))
    
    if not qid:
        flash("معرف المنتج (qid) مفقود.", "danger")
        return redirect(url_for('suppliers_product_bp.sync_supplier_products'))
    
    # تنظيف الـ qid تلقائياً لمعالجة أي تكرار محتمل (مثل qid:qumra/...)
    while qid.startswith('qid:'):
        qid = qid.replace('qid:', '', 1)
        
    if not qid.startswith('qid://') and 'qumra/Product/' in qid:
        qid = 'qid://' + qid

    # 1. جلب المنتج أولاً للتأكد من وجوده عبر الـ qid النظيف
    product = services.products.get_product_by_qid(qid)
    if not product:
        flash("❌ لم يتم العثور على المنتج", "danger")
        return redirect(url_for('suppliers_product_bp.sync_supplier_products'))

    # 2. التحقق من جدول الربط ومعالجته جذرياً لمنع أي خطأ صلاحيات
    mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()

    if user_type != 'admin':
        if not mapping:
            if supplier_id:
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
    """حفظ وتحديث منتج المورد مع المزامنة"""
    user_type = session.get('user_type')
    supplier_id = session.get('user_id') or session.get('supplier_id')

    if user_type != 'supplier' and user_type != 'admin':
        return jsonify({"status": "error", "message": "غير مصرح"}), 403
    
    try:
        qid = request.form.get('qid')
        if not qid:
            return jsonify({"status": "error", "message": "معرف المنتج (qid) مفقود."}), 400

        while qid.startswith('qid:'):
            qid = qid.replace('qid:', '', 1)

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
                services.products.update_product_info(qid, {"title": title, "sku": sku})
        except Exception as e:
            print(f"⚠️ [Warning] فشل تحديث معلومات المنتج: {e}")

        try:
            if hasattr(services.products, 'update_product_description'):
                services.products.update_product_description(qid, description)
        except Exception as e:
            print(f"⚠️ [Warning] فشل تحديث وصف المنتج: {e}")

        try:
            if hasattr(services.products, 'update_product_pricing'):
                pricing_data = {"price": price}
                if compare_price is not None:
                    pricing_data["compareAtPrice"] = compare_price
                services.products.update_product_pricing(qid, pricing_data)
        except Exception as e:
            print(f"⚠️ [Warning] فشل تحديث التسعير: {e}")

        if collection_ids:
            try:
                if hasattr(services.products, 'update_product_collection'):
                    services.products.update_product_collection(qid, collection_ids)
            except Exception as e:
                print(f"⚠️ [Warning] فشل تحديث مجموعات المنتج: {e}")

        try:
            if hasattr(services.products, 'update_product_status'):
                services.products.update_product_status(qid, status)
        except Exception as e:
            print(f"⚠️ [Warning] حدث خطأ أثناء تحديث الحالة: {e}")

        return jsonify({
            "status": "success", 
            "message": "تم حفظ وتحديث المنتج بنجاح!"
        })

    except Exception as e:
        print(f"❌ خطأ غير متوقع في save_sync_supplier_product: {e}")
        return jsonify({
            "status": "error", 
            "message": f"حدث خطأ أثناء معالجة الطلب: {str(e)}"
        }), 500


@suppliers_product_bp.route('/products/delete/<qid>', methods=['POST'])
@login_required
def delete_supplier_product(qid):
    """أرشفة وحذف منتج المورد"""
    try:
        user_type = session.get('user_type')
        supplier_id = session.get('user_id') or session.get('supplier_id')

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
