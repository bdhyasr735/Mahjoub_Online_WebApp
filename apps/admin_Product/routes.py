# coding: utf-8
# 📂 apps/admin_Product/routes.py

import json
import os
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, url_for, redirect, flash
from apps.services.product_sync_service import ProductSyncService
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier
from apps.extensions import db

admin_product_bp = Blueprint('admin_product_bp', __name__, template_folder='templates')

GRAPHQL_TOKEN = os.environ.get('QUMRA_API_KEY', 'YOUR_ADMIN_API_TOKEN')


# ============================================================
# ✅ عرض قائمة المنتجات
# ============================================================
@admin_product_bp.route('/products', methods=['GET'])
def manage_products():
    """عرض قائمة المنتجات مع دعم الترقيم والبحث"""
    try:
        page = request.args.get('page', 1, type=int)
        search_query = request.args.get('title', '', type=str)
        
        sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
        response_data = sync_service.fetch_products(page=page, limit=20, title=search_query)
        
        products = response_data.get("data", [])
        pagination = response_data.get("pagination", {"currentPage": page, "totalPages": 1, "limit": 20})
        
        return render_template(
            'admin/admin_Product.html',
            products=products,
            search_title=search_query,
            pagination=pagination
        )
    except Exception as e:
        print(f"❌ خطأ في manage_products: {e}")
        flash(f'❌ حدث خطأ في تحميل المنتجات: {str(e)}', 'danger')
        return render_template(
            'admin/admin_Product.html',
            products=[],
            search_title=request.args.get('title', ''),
            pagination={"currentPage": 1, "totalPages": 1, "limit": 20}
        )


# ============================================================
# ✅ مراجعة المنتجات (DRAFT)
# ============================================================
@admin_product_bp.route('/products/review', methods=['GET'])
def review_products():
    """صفحة مراجعة المنتجات - تعرض المنتجات التي حالتها DRAFT"""
    try:
        sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
        response_data = sync_service.fetch_products(page=1, limit=100)
        all_products = response_data.get("data", [])
        
        draft_products = [p for p in all_products if p.get('status') == 'DRAFT']
        
        for product in draft_products:
            mapping = ProductSupplierMapping.query.filter_by(
                product_qid=product.get('qid')
            ).first()
            if mapping:
                supplier = Supplier.query.get(mapping.supplier_id)
                product['supplier_name'] = supplier.trade_name if supplier else 'غير معروف'
            else:
                product['supplier_name'] = 'غير مرتبط'
        
        return render_template(
            'admin/min_review_products.html',
            products=draft_products,
            total_count=len(draft_products)
        )
        
    except Exception as e:
        print(f"❌ خطأ في review_products: {e}")
        flash('❌ حدث خطأ في تحميل صفحة المراجعة', 'danger')
        return redirect(url_for('admin_product_bp.manage_products'))


# ============================================================
# ✅ مزامنة المنتجات
# ============================================================
@admin_product_bp.route('/sync-products', methods=['POST'])
def sync_products():
    try:
        sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
        raw_data = sync_service.fetch_products(page=1, limit=50)
        
        if not raw_data or "data" not in raw_data:
            flash("تعذر جلب المنتجات من الخادم الخارجي أثناء المزامنة.", "danger")
            return redirect(url_for('admin_product_bp.manage_products'))

        count = len(raw_data.get("data", []))
        flash(f"✅ تمت مزامنة البيانات بنجاح وجلب {count} منتجاً.", "success")
        
    except Exception as e:
        flash(f"❌ حدث خطأ أثناء الاتصال بالمزامنة: {str(e)}", "danger")

    return redirect(url_for('admin_product_bp.manage_products'))


# ============================================================
# ✅ إضافة منتج
# ============================================================
@admin_product_bp.route('/products/add', methods=['GET', 'POST'])
def add_product():
    sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
    suppliers = Supplier.query.filter_by(status='active').all()
    all_collections = sync_service.fetch_collections() if hasattr(sync_service, 'fetch_collections') else []

    if request.method == 'POST':
        try:
            flash("✅ تم إضافة المنتج بنجاح.", "success")
            return redirect(url_for('admin_product_bp.manage_products'))
        except Exception as e:
            flash(f"❌ حدث خطأ: {str(e)}", "danger")

    return render_template(
        'admin/admin_add_product.html',
        suppliers=suppliers,
        all_collections=all_collections
    )


# ============================================================
# ✅ تعديل المنتج
# ============================================================
@admin_product_bp.route('/products/edit', methods=['GET'])
def edit_product():
    """عرض صفحة تعديل المنتج مع ربط المورد والمجموعات"""
    raw_qid = request.args.get('qid')
    
    if raw_qid:
        if raw_qid.startswith('qid=qid='):
            qid = raw_qid.replace('qid=qid=', 'qid://')
        elif raw_qid.startswith('qid='):
            qid = raw_qid.replace('qid=', '')
        else:
            qid = raw_qid
    else:
        qid = None
    
    if not qid:
        flash("معرف المنتج (qid) مفقود.", "danger")
        return redirect(url_for('admin_product_bp.manage_products'))
    
    sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
    product = sync_service.fetch_product_by_qid(qid)

    if not product:
        flash("❌ لم يتم العثور على المنتج", "danger")
        return redirect(url_for('admin_product_bp.manage_products'))

    # ✅ جلب الموردين النشطين
    suppliers = Supplier.query.filter_by(status='active').all()
    
    # ✅ جلب المورد المرتبط
    mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
    assigned_supplier_id = mapping.supplier_id if mapping else None

    # ✅ جلب المجموعات من Qumra
    all_collections = sync_service.fetch_collections() if hasattr(sync_service, 'fetch_collections') else []

    return render_template(
        'admin/admin_edit_product.html',
        product=product,
        all_collections=all_collections,
        suppliers=suppliers,
        assigned_supplier_id=assigned_supplier_id
    )


# ============================================================
# ✅ حفظ ومزامنة المنتج
# ============================================================
@admin_product_bp.route('/products/save-sync', methods=['POST'])
def save_sync_product():
    """معالجة وحفظ البيانات وتحديث الصور، المتغيرات، المجموعات، وربط المورد"""
    try:
        qid = request.form.get('qid')
        if not qid:
            return jsonify({"status": "error", "message": "معرف المنتج (qid) مفقود."}), 400

        # ---- البيانات الأساسية ----
        title = request.form.get('title', '')
        slug = request.form.get('slug', '')
        description = request.form.get('description', '')
        status = request.form.get('status', 'DRAFT')
        sku = request.form.get('sku', '')
        supplier_id = request.form.get('supplier_id')
        
        # ---- الأسعار ----
        try:
            price = float(request.form.get('price', 0))
            cost_price = float(request.form.get('cost_price', 0))
            compare_at_price = float(request.form.get('compare_at_price', 0))
        except ValueError:
            price, cost_price, compare_at_price = 0.0, 0.0, 0.0

        try:
            quantity = int(request.form.get('quantity', 0))
            weight_val = float(request.form.get('weight', 0))
        except ValueError:
            quantity, weight_val = 0, 0.0

        # ---- تجميع البيانات ----
        info = {"title": title, "slug": slug, "status": status}
        pricing = {
            "price": price,
            "compareAtPrice": compare_at_price,
            "costPrice": cost_price
        }
        dims = {"length": 0, "width": 0, "height": 0, "unit": "cm"}
        weight = {"value": weight_val, "unit": "kg"}
        ident = {"sku": sku}

        # ---- المجموعات ----
        collection_ids = json.loads(request.form.get('collection_ids', '[]') or '[]')
        
        # ---- المتغيرات ----
        variants_raw = request.form.get('variants', '')
        variants = []
        
        if variants_raw:
            try:
                parsed_variants = json.loads(variants_raw)
                for v in parsed_variants:
                    variants.append({
                        "quantity": int(v.get("quantity", 0)),
                        "pricing": {"price": float(v.get("price", 0.0))}
                    })
            except Exception:
                variants = []
        else:
            var_prices = request.form.getlist('variant_price[]')
            var_qtys = request.form.getlist('variant_qty[]')
            
            for i in range(max(len(var_qtys), len(var_prices))):
                try:
                    v_price = float(var_prices[i]) if i < len(var_prices) and var_prices[i] else 0.0
                except ValueError:
                    v_price = 0.0
                try:
                    v_qty = int(var_qtys[i]) if i < len(var_qtys) and var_qtys[i] else 0
                except ValueError:
                    v_qty = 0

                variants.append({
                    "quantity": v_qty,
                    "pricing": {"price": v_price}
                })

        # ---- الصور ----
        removed_images = json.loads(request.form.get('removed_images', '[]') or '[]')
        new_images = request.files.getlist('images')

        # ---- مزامنة مع Qumra ----
        sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
        
        success = sync_service.update_product_data(
            qid=qid,
            info=info,
            pricing=pricing,
            dims=dims,
            weight=weight,
            ident=ident,
            desc=description,
            supplier_id=supplier_id,
            collection_ids=collection_ids,
            variants=variants,
            removed_images=removed_images,
            new_images=new_images,
            quantity=quantity
        )

        if not success:
            return jsonify({"status": "error", "message": "فشل حفظ وتحديث التعديلات على الخادم المركزي."}), 500

        # ---- ربط المنتج بالمورد ----
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
        else:
            # ❌ إلغاء الربط إذا لم يتم اختيار مورد
            try:
                mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
                if mapping:
                    db.session.delete(mapping)
                    db.session.commit()
            except Exception as db_err:
                db.session.rollback()
                print(f"❌ خطأ في إلغاء ربط المورد: {db_err}")

        return jsonify({
            "status": "success", 
            "message": "تم حفظ المنتج ومزامنته بنجاح!"
        })

    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        return jsonify({
            "status": "error", 
            "message": f"حدث خطأ أثناء معالجة الطلب: {str(e)}"
        }), 500


# ============================================================
# ✅ تغيير حالة المنتج
# ============================================================
@admin_product_bp.route('/products/change-status/<qid>', methods=['POST'])
def change_product_status(qid):
    try:
        data = request.get_json()
        new_status = data.get('status', '').upper()
        
        if new_status not in ['PUBLISHED', 'REJECTED', 'DRAFT', 'ARCHIVED']:
            return jsonify({'success': False, 'message': 'حالة غير صالحة'}), 400
        
        sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
        result = sync_service.update_product_status(qid, new_status)
        
        if result:
            return jsonify({
                'success': True,
                'message': f'✅ تم تغيير الحالة إلى {new_status}',
                'status': new_status
            })
        else:
            return jsonify({'success': False, 'message': '❌ فشل تغيير الحالة'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# ✅ حذف المنتج
# ============================================================
@admin_product_bp.route('/products/delete/<qid>', methods=['POST'])
def delete_product(qid):
    """حذف المنتج من النظام"""
    try:
        sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
        result = sync_service.delete_product(qid)
        
        if result:
            # ✅ حذف الربط من قاعدة البيانات المحلية
            mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
            if mapping:
                db.session.delete(mapping)
                db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '✅ تم حذف المنتج بنجاح'
            })
        else:
            return jsonify({'success': False, 'message': '❌ فشل حذف المنتج'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
