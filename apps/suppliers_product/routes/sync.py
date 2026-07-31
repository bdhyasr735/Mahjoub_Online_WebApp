# coding: utf-8
# apps/suppliers_product/routes/sync.py
# مزامنة منتجات الموردين - مزامنة تدريجية آمنة

import functools
import math
import traceback
from flask import request, jsonify, session
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


@suppliers_product_bp.route('/products/sync', methods=['POST'], endpoint='sync_supplier_products')
@login_required
@analyze_render_error
def sync_supplier_products():
    """مزامنة منتجات المورد بشكل تدريجي (صفحة صفحة) لتجنب الانهيار"""
    user_type = session.get('user_type')
    supplier_id = session.get('user_id') or session.get('supplier_id')

    if user_type not in ('supplier', 'admin'):
        return jsonify({'success': False, 'message': 'غير مصرح لك بالوصول'}), 403
    
    try:
        from apps.extensions import db

        # 1. الحصول على إجمالي عدد المنتجات (بدون جلبها)
        first_page = services.products.get_products_page(1)
        if not first_page:
            return jsonify({'success': True, 'message': 'لا توجد منتجات', 'syncedCount': 0})
        
        total_items = first_page.get('pagination', {}).get('totalItems', 0)
        if total_items == 0:
            return jsonify({'success': True, 'message': 'لا توجد منتجات', 'syncedCount': 0})

        # 2. إعداد المتغيرات
        per_page = 10  # حجم الدفعة (يمكن زيادته حسب الأداء)
        total_pages = math.ceil(total_items / per_page)
        synced_count = 0
        created_count = 0
        updated_count = 0
        errors = []

        # 3. التكرار عبر الصفحات تدريجياً
        for page_num in range(1, total_pages + 1):
            print(f"🔄 مزامنة الصفحة {page_num}/{total_pages}")
            try:
                result = services.products.get_products_page(page_num)
                if not result:
                    continue
                
                page_products = result.get('data', [])
                for product in page_products:
                    if not isinstance(product, dict):
                        continue
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
            except Exception as page_error:
                print(f"⚠️ خطأ في الصفحة {page_num}: {page_error}")
                errors.append({'page': page_num, 'error': str(page_error)})

        # 4. إرجاع النتيجة النهائية
        return jsonify({
            'success': True,
            'message': f'✅ تمت مزامنة {synced_count} منتج بنجاح!',
            'syncedCount': synced_count,
            'createdCount': created_count,
            'updatedCount': updated_count,
            'errors': errors,
            'reload': True
        })

    except Exception as e:
        print(f"❌ خطأ في sync_supplier_products: {traceback.format_exc()}")
        return jsonify({
            'success': False, 
            'message': f'❌ فشل المزامنة: {str(e)}',
            'errors': [{'error': str(e)}]
        }), 500
