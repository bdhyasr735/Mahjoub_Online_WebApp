# coding: utf-8
# apps/suppliers_product/routes/sync.py

import traceback
from flask import request, jsonify, session
from flask_login import login_required, current_user
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping

try:
    from flask_wtf.csrf import csrf_exempt
except ImportError:
    def csrf_exempt(f):
        return f

@suppliers_product_bp.route('/products/sync', methods=['POST'], endpoint='sync_supplier_products')
@login_required
@csrf_exempt
def sync_supplier_products():
    from apps.extensions import db

    supplier_id = getattr(current_user, 'id', None) or session.get('supplier_id') or session.get('user_id') or session.get('_user_id')
    user_type = getattr(current_user, 'user_type', None) or getattr(current_user, 'role', None) or session.get('user_type')
    is_admin = (user_type == 'admin' or getattr(current_user, 'is_admin', False))

    if user_type not in ('supplier', 'admin') and not is_admin:
        return jsonify({'success': False, 'message': 'غير مصرح لك بالوصول'}), 403
    
    if not supplier_id:
        return jsonify({'success': False, 'message': '❌ لم يتم العثور على معرف المورد، يرجى إعادة تسجيل الدخول.'}), 400
    
    try:
        print(f"🔄 [Sync] بدء المزامنة للمورد: {supplier_id}")
        synced_count, created_count, updated_count = 0, 0, 0
        max_pages = 20  # تقليل العدد لتسريع الاستجابة وتفادي Timeout

        for page_num in range(1, max_pages + 1):
            try:
                result = services.products.get_products_page(page_num)
            except Exception as api_err:
                print(q:=f"⚠️ [Sync API Warning] خطأ في جلب الصفحة {page_num}: {api_err}")
                break

            if not result or not isinstance(result, dict):
                break
            
            page_products = result.get('data', [])
            if not page_products:
                break

            for product in page_products:
                if not isinstance(product, dict):
                    continue
                qid = product.get('qid')
                if not qid:
                    continue

                product_supplier = product.get('supplier_id') or product.get('vendor_id')
                if not is_admin and product_supplier and str(product_supplier) != str(supplier_id):
                    continue 

                with db.session.no_autoflush:
                    existing_mapping = ProductSupplierMapping.query.filter_by(product_qid=str(qid)).first()
                
                if existing_mapping and str(existing_mapping.supplier_id) != str(supplier_id) and not is_admin:
                    continue
                
                synced_count += 1
                if not existing_mapping:
                    new_mapping = ProductSupplierMapping(product_qid=str(qid), supplier_id=supplier_id)
                    db.session.add(new_mapping)
                    created_count += 1
                else:
                    updated_count += 1

        db.session.commit()
        print(f"✅ [Sync Success] تمت المزامنة بنجاح. المنتجات المرتبطة: {synced_count}")

        return jsonify({
            'success': True,
            'message': 'تمت المزامنة بنجاح',
            'syncedCount': synced_count,
            'createdCount': created_count,
            'updatedCount': updated_count,
            'has_next': False
        })

    except Exception as e:
        db.session.rollback()
        err_details = traceback.format_exc()
        print(f"❌ [Sync Critical Error]:\n{err_details}")
        return jsonify({
            'success': False, 
            'message': f'❌ حدث خطأ داخلي في الخادم: {str(e)}'
        }), 500
