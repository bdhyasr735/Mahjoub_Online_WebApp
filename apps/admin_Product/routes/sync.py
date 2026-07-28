# coding: utf-8
# 📂 apps/admin_Product/routes/sync.py
# مزامنة المنتجات

import functools
import traceback
from flask import request, jsonify, redirect, url_for, flash, session
from flask_login import login_required
from apps.admin_Product.routes import admin_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from app import db


def analyze_render_error(route_func):
    """مزيّن لتحليل أخطاء سيرفر Render"""
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
            
            if request.method == 'POST' or request.is_json:
                return jsonify({
                    "success": False,
                    "error_type": error_type,
                    "message": f"❌ خطأ في Render [{error_type}]: {error_message}"
                }), 500
            else:
                flash(f'❌ حدث خطأ أثناء المزامنة: {error_message}', 'danger')
                return redirect(url_for('admin_product_bp.manage_products_view'))
    return wrapper


@admin_product_bp.route('/products/sync', methods=['GET', 'POST'])
@login_required
@analyze_render_error
def sync_products():
    """مزامنة المنتجات مع رصد الأخطاء وإرجاع الإحصائيات التفصيلية"""
    user_type = session.get('user_type')
    if user_type != 'admin':
        if request.method == 'POST' or request.is_json:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        else:
            flash('❌ هذا القسم مخصص للإدارة فقط', 'danger')
            return redirect(url_for('admin_dashboard_bp.dashboard'))
    
    try:
        # ✅ جلب المنتجات من GraphQL
        result = services.products.get_all_products() or {}
        external_products = result.get('data', [])
        
        if not external_products:
            if request.method == 'GET':
                flash('ℹ️ لا توجد منتجات للمزامنة عبر الاتصال السحابي', 'info')
                return redirect(url_for('admin_product_bp.manage_products_view'))
            return jsonify({
                'success': True,
                'message': 'ℹ️ لا توجد منتجات للمزامنة عبر الاتصال السحابي',
                'syncedCount': 0,
                'createdCount': 0,
                'updatedCount': 0,
                'errors': []
            })
        
        synced_count = len(external_products)
        created_count = 0
        updated_count = 0
        errors = []
        
        for product in external_products:
            try:
                qid = product.get('qid')
                if not qid:
                    continue
                
                mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
                if not mapping:
                    # ✅ إنشاء وحفظ السجل الجديد في القاعدة فعلياً
                    new_mapping = ProductSupplierMapping(product_qid=qid)
                    db.session.add(new_mapping)
                    created_count += 1
                else:
                    updated_count += 1
                    
            except Exception as ex:
                errors.append({
                    'qid': product.get('qid', 'unknown'),
                    'error': str(ex)
                })
        
        # ✅ حفظ التغييرات نهائياً في قاعدة البيانات
        try:
            db.session.commit()
        except Exception as commit_err:
            db.session.rollback()
            print(f"❌ [Sync]: خطأ في حفظ السجلات: {commit_err}")
        
        # ✅ مسح Cache البحث بعد المزامنة
        try:
            services.products.clear_search_cache()
        except Exception as cache_error:
            print(f"⚠️ [Sync]: خطأ في مسح Cache: {cache_error}")
        
        if request.method == 'GET':
            flash(f'✅ تمت المزامنة: {synced_count} منتج (جديد: {created_count}, محدث: {updated_count})', 'success')
            return redirect(url_for('admin_product_bp.manage_products_view'))
        
        return jsonify({
            'success': True,
            'message': '✅ تمت مزامنة البيانات بنجاح.',
            'syncedCount': synced_count,
            'createdCount': created_count,
            'updatedCount': updated_count,
            'errors': errors
        })
        
    except Exception as e:
        print(f"❌ خطأ في sync_products: {e}")
        if request.method == 'POST' or request.is_json:
            return jsonify({
                'success': False, 
                'message': f'❌ فشل المزامنة: {str(e)}',
                'errors': [{'error': str(e)}]
            }), 500
        else:
            flash(f'❌ فشل المزامنة: {str(e)}', 'danger')
            return redirect(url_for('admin_product_bp.manage_products_view'))
