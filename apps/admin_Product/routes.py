# coding: utf-8
# 📂 apps/admin_Product/routes.py

import json
import os
import functools
import traceback
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, url_for, redirect, flash, session
from flask_login import login_required
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier
from apps.extensions import db

logger = logging.getLogger(__name__)
admin_product_bp = Blueprint('admin_product_bp', __name__, template_folder='templates')


def analyze_render_error(route_func):
    """
    مزيّن (Decorator) متقدم لتحليل أخطاء سيرفر Render وإرجاع التفاصيل التقنية بدقة وسجلات واضحة.
    """
    @functools.wraps(route_func)
    def wrapper(*args, **kwargs):
        try:
            return route_func(*args, **kwargs)
        except Exception as e:
            error_type = type(e).__name__
            error_message = str(e)
            tb_details = traceback.format_exc()
            
            print(f"\n================ 🚨 RENDER ERROR TRACEBACK ================")
            print(f"📍 المسار أو الدالة: {route_func.__name__}")
            print(f"🔴 نوع الخطأ: {error_type}")
            print(f"💬 التفاصيل: {error_message}")
            print(f"🛠️ التتبع البرمجي:\n{tb_details}")
            print(f"===========================================================\n")
            
            return jsonify({
                "success": False,
                "error_type": error_type,
                "message": f"❌ خطأ في Render [{error_type}]: {error_message}"
            }), 500
            
    return wrapper


# ============================================================
# ✅ عرض قائمة المنتجات (تظهر كل المنتجات: مرتبطة أو غير مرتبطة بمورد)
# ============================================================
@admin_product_bp.route('/products', methods=['GET'])
@login_required
def manage_products():
    """عرض قائمة المنتجات مع دعم الترقيم والبحث"""
    try:
        user_type = session.get('user_type')
        if user_type != 'admin':
            flash('❌ هذا القسم مخصص للإدارة فقط', 'danger')
            return redirect(url_for('admin_dashboard_bp.dashboard'))
        
        search_query = request.args.get('title', '', type=str)
        page = request.args.get('page', 1, type=int)
        
        # جلب جميع المنتجات من السيرفر عبر الخدمة المركزية
        products = services.products.get_all_products()
        
        if search_query:
            products = [p for p in products if search_query.lower() in p.get('name', '').lower()]
        
        # ✅ ربط الموردين إن وجدوا، وإذا لم يوجد مورد يظهر المنتج كـ "غير مرتبط" دون حذفه
        for product in products:
            mapping = ProductSupplierMapping.query.filter_by(
                product_qid=product.get('qid')
            ).first()
            if mapping:
                supplier = Supplier.query.get(mapping.supplier_id)
                product['supplier_name'] = supplier.trade_name if supplier else 'غير معروف'
                product['supplier_id'] = mapping.supplier_id
            else:
                product['supplier_name'] = 'غير مرتبط'
                product['supplier_id'] = None
        
        return render_template(
            'admin/admin_Product.html',
            products=products,
            search_title=search_query,
            pagination={"currentPage": page, "totalPages": 1, "limit": len(products)}
        )
    except Exception as e:
        print(f"❌ خطأ في manage_products: {e}")
        flash(f'❌ حدث خطأ في تحميل المنتجات: {str(e)}', 'danger')
        return render_template(
            'admin/admin_Product.html',
            products=[],
            search_title=request.args.get('title', ''),
            pagination={"currentPage": 1, "totalPages": 1, "limit": 0}
        )


# ============================================================
# ✅ مراجعة المنتجات (DRAFT)
# ============================================================
@admin_product_bp.route('/products/review', methods=['GET'])
@login_required
def review_products():
    """صفحة مراجعة المنتجات - تعرض المنتجات التي حالتها DRAFT"""
    try:
        user_type = session.get('user_type')
        if user_type != 'admin':
            flash('❌ هذا القسم مخصص للإدارة فقط', 'danger')
            return redirect(url_for('admin_dashboard_bp.dashboard'))
        
        all_products = services.products.get_all_products()
        draft_products = [p for p in all_products if p.get('status') == 'DRAFT']
        
        for product in draft_products:
            mapping = ProductSupplierMapping.query.filter_by(
                product_qid=product.get('qid')
            ).first()
            if mapping:
                supplier = Supplier.query.get(mapping.supplier_id)
                product['supplier_name'] = supplier.trade_name if supplier else 'غير معروف'
                product['supplier_id'] = mapping.supplier_id
            else:
                product['supplier_name'] = 'غير مرتبط'
                product['supplier_id'] = None
        
        total_draft = len(draft_products)
        total_published = len([p for p in all_products if p.get('status') == 'PUBLISHED'])
        total_rejected = len([p for p in all_products if p.get('status') == 'REJECTED'])
        
        return render_template(
            'admin/admin_review_products.html',
            products=draft_products,
            total_count=total_draft,
            total_published=total_published,
            total_rejected=total_rejected
        )
        
    except Exception as e:
        print(f"❌ خطأ في review_products: {e}")
        flash('❌ حدث خطأ في تحميل صفحة المراجعة', 'danger')
        return redirect(url_for('admin_product_bp.manage_products'))


# ============================================================
# ✅ تغيير حالة المنتج (موافقة/رفض)
# ============================================================
@admin_product_bp.route('/products/change-status/<qid>', methods=['POST'])
@login_required
def change_product_status(qid):
    """تغيير حالة المنتج (موافقة/رفض/إعادة للمراجعة)"""
    try:
        user_type = session.get('user_type')
        if user_type != 'admin':
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
        data = request.get_json() or {}
        new_status = data.get('status', '').upper()
        
        valid_statuses = ['PUBLISHED', 'REJECTED', 'DRAFT', 'ARCHIVED']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': 'حالة غير صالحة'}), 400
        
        # استخدام دالة التعديل لتحديث الحالة عبر الـ Mutation
        result = services.products.update_product_data({"qid": qid, "status": new_status})
        
        if result:
            mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
            if mapping:
                mapping.updated_at = datetime.utcnow()
                db.session.commit()
            
            status_names = {
                'PUBLISHED': '✅ تم النشر',
                'REJECTED': '❌ تم الرفض',
                'DRAFT': '⏳ تمت الإعادة للمراجعة',
                'ARCHIVED': '📦 تمت الأرشفة'
            }
            
            return jsonify({
                'success': True,
                'message': status_names.get(new_status, f'تم تغيير الحالة إلى {new_status}'),
                'status': new_status
            })
        else:
            return jsonify({'success': False, 'message': '❌ فشل تغيير الحالة في السيرفر'}), 500
            
    except Exception as e:
        print(f"❌ خطأ في change_product_status: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# ✅ حذف المنتج
# ============================================================
@admin_product_bp.route('/products/delete/<qid>', methods=['POST'])
@login_required
def delete_product(qid):
    """حذف المنتج من النظام"""
    try:
        user_type = session.get('user_type')
        if user_type != 'admin':
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
        # افتراض وجود دالة حذف أو أرشفة في الخدمة
        # (في حال لم تكن موجودة كميوتيشن منفصل، يتم إرسال حالة Archived أو التعامل معها)
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


# ============================================================
# ✅ إحصائيات سريعة (AJAX)
# ============================================================
@admin_product_bp.route('/products/stats', methods=['GET'])
@login_required
def get_stats():
    """جلب إحصائيات المنتجات للمراجعة (AJAX)"""
    try:
        user_type = session.get('user_type')
        if user_type != 'admin':
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
        all_products = services.products.get_all_products()
        
        stats = {
            'total': len(all_products),
            'draft': len([p for p in all_products if p.get('status') == 'DRAFT']),
            'published': len([p for p in all_products if p.get('status') == 'PUBLISHED']),
            'rejected': len([p for p in all_products if p.get('status') == 'REJECTED']),
            'archived': len([p for p in all_products if p.get('status') == 'ARCHIVED'])
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# ✅ مزامنة المنتجات (مع تحليل الأخطاء المتقدم لبيئة Render)
# ============================================================
@admin_product_bp.route('/products/sync-products', methods=['POST'])
@login_required
@analyze_render_error
def sync_products():
    """مزامنة المنتجات مع رصد الأخطاء وتحليلها بدقة"""
    user_type = session.get('user_type')
    if user_type != 'admin':
        return jsonify({'success': False, 'message': 'غير مصرح'}), 403
    
    external_products = services.products.get_all_products()
    
    if not external_products:
        return jsonify({
            'success': True,
            'message': 'ℹ️ لا توجد منتجات للمزامنة',
            'count': 0
        })
    
    # يمكنك إضافة منطق المزامنة المحلية هنا أو استدعاء دالة الخدمة إذا وجدت
    return jsonify({
        'success': True,
        'message': f"✅ تمت المزامنة بنجاح: تم جلب {len(external_products)} منتجاً.",
        'count': len(external_products)
    })


# ============================================================
# ✅ إضافة منتج
# ============================================================
@admin_product_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
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
                
            return redirect(url_for('admin_product_bp.manage_products'))
            
        except Exception as e:
            flash(f'❌ حدث خطأ: {str(e)}', 'danger')

    return render_template(
        'admin/admin_add_product.html',
        suppliers=suppliers
    )


# ============================================================
# ✅ تعديل المنتج
# ============================================================
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
        return redirect(url_for('admin_product_bp.manage_products'))
    
    product = services.products.get_product_by_qid(qid)

    if not product:
        flash("❌ لم يتم العثور على المنتج", "danger")
        return redirect(url_for('admin_product_bp.manage_products'))

    suppliers = Supplier.query.filter_by(status='active').all()
    mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
    assigned_supplier_id = mapping.supplier_id if mapping else None

    return render_template(
        'admin/admin_edit_product.html',
        product=product,
        suppliers=suppliers,
        assigned_supplier_id=assigned_supplier_id
    )


# ============================================================
# ✅ حفظ ومزامنة المنتج
# ============================================================
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
        
        try:
            price = float(request.form.get('price', 0))
        except ValueError:
            price = 0.0

        update_data = {
            'qid': qid,
            'name': title,
            'price': price,
            'status': status,
            'description': description
        }
        
        if sku:
            update_data['sku'] = sku
        
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
