# coding: utf-8
# apps/admin_Product/routes/crud.py
# إضافة - تعديل - حذف المنتجات

from flask import render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required
from apps.admin_Product.routes import admin_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier
from apps.extensions import db
from datetime import datetime


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
            
            product_data = {
                'name': request.form.get('title', ''),
                'price': price_val,
                'status': request.form.get('status', 'DRAFT'),
                'description': request.form.get('description', '')
            }
            
            if request.form.get('sku'):
                product_data['sku'] = request.form.get('sku')
            
            result = services.products.create_product_data(product_data)
            
            if result and 'qid' in result:
                supplier_id = request.form.get('supplier_id')
                if supplier_id:
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
    """عرض صفحة تعديل المنتج مع الخيارات (الحل النهائي والآمن)"""
    user_type = session.get('user_type')
    if user_type != 'admin':
        flash('❌ هذا القسم مخصص للإدارة فقط', 'danger')
        return redirect(url_for('admin_dashboard_bp.dashboard'))
    
    qid = request.args.get('qid')
    
    if not qid:
        flash("معرف المنتج (qid) مفقود.", "danger")
        return redirect(url_for('admin_product_bp.manage_products_view'))
    
    # ✅ محاولة جلب المنتج مع الخيارات والمتغيرات (الحل الآمن)
    try:
        # استخدم service.variants (الذي تم تعريفه في __init__.py)
        product = services.variants.get_product_with_options_and_variants(qid)
    except Exception as e:
        print(f"❌ [ERROR] فشل جلب المنتج مع الخيارات: {e}")
        flash(f"❌ حدث خطأ أثناء تحميل بيانات المنتج.", "danger")
        return redirect(url_for('admin_product_bp.manage_products_view'))

    if not product:
        flash("❌ لم يتم العثور على المنتج", "danger")
        return redirect(url_for('admin_product_bp.manage_products_view'))

    # جلب البيانات الإضافية
    suppliers = Supplier.query.filter_by(status='active').all()
    mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
    assigned_supplier_id = mapping.supplier_id if mapping else None

    # ✅ جلب جميع المجموعات للقائمة المنسدلة
    try:
        all_collections = services.collections.get_all_collections() if hasattr(services, 'collections') else []
        print(f"🔍 [DEBUG] Collections loaded: {len(all_collections)}")
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
    """معالجة وحفظ البيانات"""
    user_type = session.get('user_type')
    if user_type != 'admin':
        return jsonify({"status": "error", "message": "غير مصرح"}), 403
    
    try:
        qid = request.form.get('qid')
        if not qid:
            return jsonify({"status": "error", "message": "معرف المنتج (qid) مفقود."}), 400

        title = request.form.get('title', '')
        description = request.form.get('description', '')
        status = request.form.get('status', 'DRAFT')
        sku = request.form.get('sku', '')
        supplier_id = request.form.get('supplier_id')
        quantity = request.form.get('quantity', 0)
        
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
        print(f"🔍 [DEBUG] Collection IDs received: {collection_ids}")

        update_data = {
            'qid': qid,
            'name': title,
            'price': price,
            'status': status,
            'description': description,
            'quantity': int(quantity) if quantity else 0,
            'seo': {
                'title': seo_title,
                'description': seo_description,
                'keywords': seo_keywords
            }
        }
        
        if sku:
            update_data['sku'] = sku
        
        if compare_price is not None:
            update_data['compareAtPrice'] = compare_price
        
        if collection_ids:
            update_data['collectionIds'] = collection_ids
        
        result = services.products.update_product_data(update_data)

        if not result:
            return jsonify({"status": "error", "message": "فشل حفظ التعديلات."}), 500

        if supplier_id:
            try:
                supplier_id_int = int(supplier_id)
                supplier = Supplier.query.get(supplier_id_int)
                
                if not supplier:
                    return jsonify({
                        "status": "error",
                        "message": f"المورد برقم {supplier_id} غير موجود."
                    }), 404
                
                mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
                if mapping:
                    mapping.supplier_id = supplier_id_int
                    mapping.status = 'active'
                    mapping.updated_at = datetime.utcnow()
                else:
                    mapping = ProductSupplierMapping(
                        product_qid=qid,
                        supplier_id=supplier_id_int,
                        status='active'
                    )
                    db.session.add(mapping)
                db.session.commit()
                
            except ValueError:
                return jsonify({
                    "status": "error",
                    "message": "معرف المورد غير صحيح."
                }), 400
            except Exception as db_err:
                db.session.rollback()
                print(f"❌ خطأ في ربط المورد: {db_err}")
                return jsonify({
                    "status": "error",
                    "message": f"فشل ربط المنتج بالمورد: {str(db_err)}"
                }), 500

        return jsonify({
            "status": "success", 
            "message": "تم حفظ المنتج بنجاح!"
        })

    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        return jsonify({
            "status": "error", 
            "message": f"حدث خطأ أثناء معالجة الطلب: {str(e)}"
        }), 500


@admin_product_bp.route('/products/delete/<qid>', methods=['POST'])
@login_required
def delete_product(qid):
    """حذف المنتج من النظام"""
    try:
        user_type = session.get('user_type')
        if user_type != 'admin':
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
        result = services.products.update_product_data({"qid": qid, "status": "ARCHIVED"})
        
        if result:
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
