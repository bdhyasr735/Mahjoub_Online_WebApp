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
        # قراءة الصفحة الحالية المرسلة من النافذة المنبثقة مع حماية ضد البيانات الفارغة
        req_data = request.get_json(silent=True) or {}
        page_num = int(req_data.get('page', 1))

        print(f"🔄 [Sync] جاري مزامنة الصفحة {page_num} للمورد: {supplier_id}")

        # حماية إضافية للخدمة الخارجية لمنع انهيار الخادم (رمز 500)
        try:
            result = services.products.get_products_page(page_num)
        except Exception as svc_err:
            print(f"⚠️ [Sync Service Error]: {svc_err}")
            result = {}

        if not result or not isinstance(result, dict):
            return jsonify({
                'success': True,
                'syncedCount': 0,
                'has_next': False,
                'total_pages': page_num,
                'message': 'انتهت الصفحات أو لم يتم استجابة من الخدمة'
            })

        page_products = result.get('data', [])
        pagination = result.get('pagination', {})
        total_pages = pagination.get('totalPages', pagination.get('total_pages', 1))
        
        synced_count = 0
        created_count = 0
        updated_count = 0

        for product in page_products:
            if not isinstance(product, dict):
                continue
            
            # البحث عن معرف المنتج بأكثر من احتمال لتجنب الفقدان
            qid = product.get('qid') or product.get('id')
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
                new_mapping = ProductSupplierMapping(product_qid=str(qid), supplier_id=supplier_id, status='active')
                db.session.add(new_mapping)
                created_count += 1
            else:
                updated_count += 1

        db.session.commit()

        # تحديد هل توجد صفحة تالية للمتابعة في النافذة المنبثقة
        has_next = page_num < total_pages

        return jsonify({
            'success': True,
            'message': 'تمت المزامنة بنجاح',
            'syncedCount': synced_count,
            'createdCount': created_count,
            'updatedCount': updated_count,
            'has_next': has_next,
            'next_page': page_num + 1,
            'total_pages': total_pages
        })

    except Exception as e:
        db.session.rollback()
        err_details = traceback.format_exc()
        print(f"❌ [Sync Critical Error]:\n{err_details}")
        return jsonify({
            'success': False, 
            'message': f'❌ خطأ في الخادم: {str(e)}'
        }), 500
