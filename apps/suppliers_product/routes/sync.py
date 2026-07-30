# coding: utf-8
# apps/suppliers_product/routes/sync.py
# مزامنة منتجات الموردين

import functools
import traceback
from flask import request, jsonify, redirect, url_for, flash, session
from flask_login import login_required
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping


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
            
            return jsonify({
                "success": False,
                "error_type": error_type,
                "message": f"❌ خطأ في Render [{error_type}]: {error_message}"
            }), 500
    return wrapper


@suppliers_product_bp.route('/products/sync', methods=['GET', 'POST'])
@login_required
@analyze_render_error
def sync_supplier_products():
    """مزامنة منتجات المورد الحالي مع رصد الأخطاء وإرجاع الإحصائيات التفصيلية"""
    user_type = session.get('user_type')
    supplier_id = session.get('user_id') or session.get('supplier_id') # معرف المورد الحالي في الجلسة

    # التحقق من أن المستخدم مسجل كـ مورد
    if user_type != 'supplier' and user_type != 'admin':
        if request.method == 'POST':
            return jsonify({'success': False, 'message': 'غير مصرح لك بالوصول'}), 403
        else:
            flash('❌ هذا القسم مخصص للموردين فقط', 'danger')
            return redirect(url_for('suppliers_dashboard_bp.dashboard'))
    
    try:
        # ✅ جلب المنتجات من الخدمات (دعم الطريقتين لضمان نجاح الجلب)
        result = services.products.get_all_products() if hasattr(services.products, 'get_all_products') else {}
        if isinstance(result, dict):
            external_products = result.get('data', []) or result.get('products', [])
        elif isinstance(result, list):
            external_products = result
        else:
            external_products = services.products.fetch_all_products_for_search() if hasattr(services.products, 'fetch_all_products_for_search') else []
        
        if not external_products:
            if request.method == 'GET':
                flash('ℹ️ لا توجد منتجات جديدة للمزامنة', 'info')
                return redirect(url_for('suppliers_product_bp.manage_supplier_products_view'))
            return jsonify({
                'success': True,
                'message': 'ℹ️ لا توجد منتجات جديدة للمزامنة',
                'syncedCount': 0,
                'createdCount': 0,
                'updatedCount': 0,
                'errors': []
            })
        
        synced_count = 0
        created_count = 0
        updated_count = 0
        errors = []
        
        for product in external_products:
            try:
                qid = product.get('qid')
                if not qid:
                    continue
                
                # التحقق هل المنتج مرتبط بهذا المورد أو مسجل في النظام
                mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
                
                if supplier_id and hasattr(mapping, 'supplier_id') and mapping.supplier_id:
                    if str(mapping.supplier_id) != str(supplier_id) and user_type != 'admin':
                        continue # تخطي المنتجات التي لا تخص هذا المورد
                
                synced_count += 1
                if not mapping:
                    created_count += 1
                    # ربط المنتج تلقائياً بالمورد الحالي إذا لم يكن مربوطاً
                    if supplier_id and user_type == 'supplier':
                        new_mapping = ProductSupplierMapping(product_qid=qid, supplier_id=supplier_id)
                        from apps.extensions import db
                        db.session.add(new_mapping)
                        db.session.commit()
                else:
                    updated_count += 1
                    
            except Exception as ex:
                errors.append({
                    'qid': product.get('qid', 'unknown'),
                    'error': str(ex)
                })
        
        if request.method == 'GET':
            flash(f'✅ تمت المزامنة: {synced_count} منتج (جديد: {created_count}, محدث: {updated_count})', 'success')
            return redirect(url_for('suppliers_product_bp.manage_supplier_products_view'))
        
        return jsonify({
            'success': True,
            'message': '✅ تمت مزامنة منتجات المورد بنجاح.',
            'syncedCount': synced_count,
            'createdCount': created_count,
            'updatedCount': updated_count,
            'errors': errors
        })
        
    except Exception as e:
        print(f"❌ خطأ في sync_supplier_products: {e}")
        if request.method == 'POST':
            return jsonify({
                'success': False, 
                'message': f'❌ فشل المزامنة: {str(e)}',
                'errors': [{'error': str(e)}]
            }), 500
        else:
            flash(f'❌ فشل المزامنة: {str(e)}', 'danger')
            return redirect(url_for('suppliers_product_bp.manage_supplier_products_view'))
