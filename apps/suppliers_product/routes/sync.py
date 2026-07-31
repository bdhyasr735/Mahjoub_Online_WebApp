# coding: utf-8
# apps/suppliers_product/routes/sync.py
# مزامنة منتجات الموردين - مع جلب جميع المنتجات وتحديث الواجهة

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


@suppliers_product_bp.route('/products/sync', methods=['POST'])
@login_required
@analyze_render_error
def sync_supplier_products():
    """مزامنة منتجات المورد مع جلب جميع المنتجات من كافة الصفحات"""
    user_type = session.get('user_type')
    supplier_id = session.get('user_id') or session.get('supplier_id')

    if user_type not in ('supplier', 'admin'):
        return jsonify({'success': False, 'message': 'غير مصرح لك بالوصول'}), 403
    
    try:
        # ✅ 1. جلب جميع المنتجات من جميع الصفحات (حلقة تكرار ذكية)
        all_external_products = []
        current_page = 1
        has_next = True
        max_pages = 100  # الحد الأقصى للصفحات للحماية
        
        while has_next and current_page <= max_pages:
            try:
                result = services.products.get_products_page(current_page)
                if not result:
                    break
                page_products = result.get('data', [])
                pagination = result.get('pagination', {})
                
                all_external_products.extend(page_products)
                has_next = pagination.get('hasNextPage', False)
                current_page += 1
            except Exception as api_fetch_err:
                print(f"⚠️ تحذير أثناء جلب الصفحة {current_page}: {api_fetch_err}")
                break
        
        if not all_external_products:
            return jsonify({
                'success': True,
                'message': 'ℹ️ لا توجد منتجات جديدة للمزامنة',
                'syncedCount': 0,
                'createdCount': 0,
                'updatedCount': 0,
                'errors': []
            })
        
        # ✅ 2. معالجة المنتجات (ربطها بالمورد أو تحديثها)
        synced_count = 0
        created_count = 0
        updated_count = 0
        errors = []
        
        from apps.extensions import db
        
        for product in all_external_products:
            if not isinstance(product, dict):
                continue
            try:
                qid = product.get('qid')
                if not qid:
                    continue
                
                mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
                
                if supplier_id and mapping and mapping.supplier_id:
                    if str(mapping.supplier_id) != str(supplier_id) and user_type != 'admin':
                        continue
                
                synced_count += 1
                if not mapping:
                    created_count += 1
                    if supplier_id and user_type == 'supplier':
                        new_mapping = ProductSupplierMapping(product_qid=qid, supplier_id=supplier_id)
                        db.session.add(new_mapping)
                        db.session.commit()
                else:
                    updated_count += 1
                    
            except Exception as ex:
                errors.append({
                    'qid': product.get('qid', 'unknown'),
                    'error': str(ex)
                })
        
        # ✅ 3. إرجاع النتيجة
        return jsonify({
            'success': True,
            'message': '✅ تمت مزامنة منتجات المورد بنجاح وجلب جميع المنتجات.',
            'syncedCount': synced_count,
            'createdCount': created_count,
            'updatedCount': updated_count,
            'errors': errors,
            'reload': True  # 🟢 إشارة للواجهة لإعادة التحميل فوراً
        })
        
    except Exception as e:
        print(f"❌ خطأ في sync_supplier_products: {e}")
        return jsonify({
            'success': False, 
            'message': f'❌ فشل المزامنة: {str(e)}',
            'errors': [{'error': str(e)}]
        }), 500
