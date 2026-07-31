# coding: utf-8
# apps/suppliers_product/routes/sync.py
# مزامنة منتجات الموردين - مزامنة تدريجية آمنة وذكية

import functools
import math
import traceback
from flask import request, jsonify, session, current_app
from flask_login import login_required
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping

# ✅ حل ذكي لـ CSRF
try:
    from flask_wtf.csrf import csrf_exempt
except ImportError:
    def csrf_exempt(f):
        return f


def analyze_render_error(route_func):
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
@csrf_exempt
@analyze_render_error
def sync_supplier_products():
    """مزامنة منتجات المورد بشكل تدريجي وذكي"""
    user_type = session.get('user_type')
    supplier_id = session.get('user_id') or session.get('supplier_id')

    if user_type not in ('supplier', 'admin'):
        return jsonify({'success': False, 'message': 'غير مصرح لك بالوصول'}), 403
    
    try:
        from apps.extensions import db

        print(f"🔍 [Sync] بدء المزامنة للمورد {supplier_id}")

        # ✅ 1. حساب إجمالي الصفحات من GraphQL (جلب كل المنتجات)
        first_page = services.products.get_products_page(1)
        if not first_page:
            return jsonify({'success': True, 'message': 'لا توجد منتجات', 'syncedCount': 0})
        
        total_items = first_page.get('pagination', {}).get('totalItems', 0)
        if total_items == 0:
            return jsonify({'success': True, 'message': 'لا توجد منتجات', 'syncedCount': 0})

        per_page = 10
        total_pages = math.ceil(total_items / per_page)
        
        # ✅ 2. جلب جميع المنتجات من GraphQL وربطها بالمورد
        synced_count = 0
        created_count = 0
        updated_count = 0
        errors = []

        for page_num in range(1, total_pages + 1):
            print(f"🔄 [Sync] معالجة الصفحة {page_num}/{total_pages}")
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
                    
                    # ✅ التحقق مما إذا كان المنتج مرتبطاً بمورد آخر
                    existing_mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
                    
                    # إذا كان المنتج مرتبطاً بمورد مختلف (والمستخدم ليس أدمن)، نتجاهله
                    if existing_mapping and existing_mapping.supplier_id != supplier_id and user_type != 'admin':
                        continue
                    
                    synced_count += 1
                    if not existing_mapping:
                        # إنشاء ربط جديد
                        new_mapping = ProductSupplierMapping(product_qid=qid, supplier_id=supplier_id)
                        db.session.add(new_mapping)
                        created_count += 1
                    else:
                        # تحديث التاريخ (موجود بالفعل)
                        updated_count += 1

                db.session.commit()  # حفظ بعد كل صفحة لتخفيف الحمل

            except Exception as page_error:
                print(f"⚠️ [Sync] خطأ في الصفحة {page_num}: {page_error}")
                errors.append({'page': page_num, 'error': str(page_error)})

        print(f"✅ [Sync] تمت المزامنة بنجاح. تم إنشاء {created_count} منتج جديد، تحديث {updated_count} منتج.")

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
        print(f"❌ [Sync] خطأ غير متوقع: {traceback.format_exc()}")
        return jsonify({
            'success': False, 
            'message': f'❌ فشل المزامنة: {str(e)}',
            'errors': [{'error': str(e)}]
        }), 500
