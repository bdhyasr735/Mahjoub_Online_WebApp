# coding: utf-8
# apps/suppliers_product/routes/sync.py
# مزامنة منتجات الموردين - تم إصلاحها لجلب جميع الصفحات

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
    supplier_id = session.get('user_id') or session.get('supplier_id')

    # التحقق من أن المستخدم مسجل كـ مورد أو مدير
    if user_type != 'supplier' and user_type != 'admin':
        if request.method == 'POST':
            return jsonify({'success': False, 'message': 'غير مصرح لك بالوصول'}), 403
        else:
            flash('❌ هذا القسم مخصص للموردين فقط', 'danger')
            return redirect(url_for('suppliers_dashboard_bp.dashboard'))
    
    try:
        # ✅ 1. جلب جميع المنتجات من الخدمة (صفحة صفحة)
        all_external_products = []
        current_page = 1
        page_limit = 100  # يمكنك زيادة هذا الرقم لتسريع الجلب
        has_more_pages = True
        
        while has_more_pages:
            try:
                # هنا يجب أن تدعم الخدمة استقبال صفحة. إذا كانت لا تدعم، يجب عليك توسيع service
                # افترضنا أن services.products.get_all_products يقبل `page` و `limit`
                result = services.products.get_all_products(page=current_page, limit=page_limit)
                
                if isinstance(result, dict):
                    page_products = result.get('data', []) or result.get('products', [])
                    # التحقق من وجود صفحات أخرى (إذا كانت الخدمة ترجع pagination info)
                    pagination_info = result.get('pagination', {})
                    has_more_pages = pagination_info.get('hasNextPage', False)
                    total_pages = pagination_info.get('totalPages', 0)
                elif isinstance(result, list):
                    page_products = result
                    # إذا كانت القائمة فارغة، نعتبر أننا وصلنا للنهاية
                    has_more_pages = False
                else:
                    page_products = []
                    has_more_pages = False
                
                all_external_products.extend(page_products)
                
                # إذا لم يكن هناك معلومات ترقيم، نعتبر أننا انتهينا
                if not has_more_pages:
                    break
                    
                current_page += 1
                
            except Exception as api_fetch_err:
                print(f"⚠️ تحذير أثناء جلب الصفحة {current_page}: {api_fetch_err}")
                break
        
        if not all_external_products:
            if request.method == 'GET':
                flash('ℹ️ لا توجد منتجات جديدة للمزامنة', 'info')
                return redirect(url_for('suppliers_product_bp.list_supplier_products'))
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
        
        for product in all_external_products:
            if not isinstance(product, dict):
                continue
            try:
                qid = product.get('qid')
                if not qid:
                    continue
                
                # التحقق هل المنتج مرتبط بهذا المورد أو مسجل في النظام
                mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
                
                if supplier_id and hasattr(mapping, 'supplier_id') and mapping and mapping.supplier_id:
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
            return redirect(url_for('suppliers_product_bp.list_supplier_products'))
        
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
            return redirect(url_for('suppliers_product_bp.list_supplier_products'))
