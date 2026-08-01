# coding: utf-8
# apps/admin_Product/routes/crud.py

from flask import render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required
from apps.admin_Product.routes import admin_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier
from apps.extensions import db
from datetime import datetime
import json


@admin_product_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """إضافة منتج جديد"""
    user_type = session.get('user_type')
    if user_type != 'admin':
        flash('❌ هذا القسم مخصص للإدارة فقط', 'danger')
        return redirect(url_for('admin_dashboard_bp.dashboard'))
    
    suppliers = Supplier.query.filter_by(status='active').all()
    
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
                supplier_id = request.form.get('supplier_id')
                if supplier_id and supplier_id.strip():
                    mapping = ProductSupplierMapping(
                        product_qid=result['qid'],
                        supplier_id=int(supplier_id),
                        status='active'
                    )
                    db.session.add(mapping)
                    db.session.commit()
                
                flash('✅ تم إضافة المنتج بنجاح.', 'success')
            else:
                flash('❌ فشل إضافة المنتج', 'danger')
                
            return redirect(url_for('admin_product_bp.manage_products_view'))
            
        except Exception as e:
            flash(f'❌ حدث خطأ: {str(e)}', 'danger')

    return render_template(
        'admin/admin_add_product.html',
        suppliers=suppliers
    )


@admin_product_bp.route('/products/edit', methods=['GET'])
@login_required
def edit_product():
    """عرض صفحة تعديل المنتج"""
    user_type = session.get('user_type')
    if user_type != 'admin':
        flash('❌ هذا القسم مخصص للإدارة فقط', 'danger')
        return redirect(url_for('admin_dashboard_bp.dashboard'))
    
    qid = request.args.get('qid')
    
    if not qid:
        flash("معرف المنتج (qid) مفقود.", "danger")
        return redirect(url_for('admin_product_bp.manage_products_view'))
    
    product = services.products.get_product_by_qid(qid)
    if not product:
        flash("❌ لم يتم العثور على المنتج", "danger")
        return redirect(url_for('admin_product_bp.manage_products_view'))

    # تنظيف الخيارات (Options) واستخراجها بشكل آمن
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
            print(f"⚠️ [Edit Product] تعذر جلب الخيارات عبر خدمة variants: {e}")

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

    suppliers = Supplier.query.filter_by(status='active').all()
    mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
    assigned_supplier_id = mapping.supplier_id if mapping else None

    try:
        all_collections = services.collections.get_all_collections() if hasattr(services, 'collections') else []
    except Exception as e:
        print(f"❌ [DEBUG] Error loading collections: {e}")
        all_collections = []

    return render_template(
        'admin/admin_edit_product.html',
        product=product,
        suppliers=suppliers,
        assigned_supplier_id=assigned_supplier_id,
        all_collections=all_collections
    )


@admin_product_bp.route('/products/save-sync', methods=['POST'])
@login_required
def save_sync_product():
    """حفظ المنتج مع مزامنة المتغيرات والحالة (محسن ومجزأ ليتوافق مع الـ API)"""
    user_type = session.get('user_type')
    if user_type != 'admin':
        return jsonify({"status": "error", "message": "غير مصرح"}), 403
    
    try:
        qid = request.form.get('qid')
        if not qid:
            return jsonify({"status": "error", "message": "معرف المنتج (qid) مفقود."}), 400

        title = request.form.get('title', '')
        description = request.form.get('description', '')
        raw_status = request.form.get('status', 'DRAFT')
        status = raw_status.upper() if raw_status else 'DRAFT'
        sku = request.form.get('sku', '')
        supplier_id = request.form.get('supplier_id')
        
        seo_title = request.form.get('seo_title', '')
        seo_description = request.form.get('seo_description', '')
        seo_keywords = request.form.get('seo_keywords', '')
        
        try:
            price = float(request.form.get('price', 0))
        except ValueError:
            price = 0.0
        
        try:
            compare_price = float(request.form.get('compare_price', 0)) if request.form.get('compare_price') else None
        except ValueError:
            compare_price = None

        collection_ids = request.form.getlist('collection_ids')

        # ============================================================
        # ✅ 1. حفظ المورد محلياً
        # ============================================================
        try:
            supplier_id_clean = int(supplier_id) if supplier_id and supplier_id.strip() else None
            mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
            
            if not supplier_id_clean:
                if mapping:
                    db.session.delete(mapping)
                    db.session.commit()
            else:
                supplier = Supplier.query.get(supplier_id_clean)
                if supplier:
                    if mapping:
                        mapping.supplier_id = supplier_id_clean
                        mapping.status = 'active'
                        mapping.updated_at = datetime.utcnow()
                    else:
                        mapping = ProductSupplierMapping(
                            product_qid=qid,
                            supplier_id=supplier_id_clean,
                            status='active'
                        )
                        db.session.add(mapping)
                    db.session.commit()
        except Exception as db_err:
            db.session.rollback()
            print(f"⚠️ [Supplier] خطأ أثناء حفظ المورد: {db_err}")

        # ============================================================
        # ✅ 2. تحديث البيانات عبر الـ Mutations المجزأة للـ GraphQL
        # ============================================================
        
        # أ. تحديث المعلومات الأساسية (الاسم والـ SKU)
        try:
            if hasattr(services.products, 'update_product_info'):
                services.products.update_product_info(qid, {"title": title, "sku": sku})
        except Exception as e:
            print(f"⚠️ [Warning] فشل تحديث معلومات المنتج: {e}")

        # ب. تحديث الوصف
        try:
            if hasattr(services.products, 'update_product_description'):
                services.products.update_product_description(qid, description)
        except Exception as e:
            print(f"⚠️ [Warning] فشل تحديث وصف المنتج: {e}")

        # ج. تحديث التسعير
        try:
            if hasattr(services.products, 'update_product_pricing'):
                pricing_data = {"price": price}
                if compare_price is not None:
                    pricing_data["compareAtPrice"] = compare_price
                services.products.update_product_pricing(qid, pricing_data)
        except Exception as e:
            print(f"⚠️ [Warning] فشل تحديث التسعير: {e}")

        # د. تحديث الـ SEO
        try:
            if hasattr(services.products, 'update_product_seo'):
                services.products.update_product_seo(qid, {
                    "title": seo_title,
                    "description": seo_description,
                    "keywords": seo_keywords
                })
        except Exception as e:
            print(f"⚠️ [Warning] فشل تحديث الـ SEO: {e}")

        # هـ. تحديث المجموعات
        if collection_ids:
            try:
                if hasattr(services.products, 'update_product_collection'):
                    services.products.update_product_collection(qid, collection_ids)
            except Exception as e:
                print(f"⚠️ [Warning] فشل تحديث مجموعات المنتج: {e}")

        # و. تحديث الحالة
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
        print(f"❌ خطأ غير متوقع في save_sync_product: {e}")
        return jsonify({
            "status": "error", 
            "message": f"حدث خطأ أثناء معالجة الطلب: {str(e)}"
        }), 500


@admin_product_bp.route('/products/delete/<qid>', methods=['POST'])
@login_required
def delete_product(qid):
    """حذف وأرشفة المنتج من النظام"""
    try:
        user_type = session.get('user_type')
        if user_type != 'admin':
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
        result = services.products.update_product_status(qid, "ARCHIVED")
        
        if result and result.get('success'):
            mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
            if mapping:
                db.session.delete(mapping)
                db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '✅ تم حذف/أرشفة المنتج بنجاح'
            })
        else:
            return jsonify({'success': False, 'message': '❌ فشل حذف المنتج'}), 500
            
    except Exception as e:
        print(f"❌ خطأ في delete_product: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
