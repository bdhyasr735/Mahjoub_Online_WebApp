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
        return jsonify({'success': False, 'message': 'غير مصرح لك بالوصول'}, 403)
    
    if not supplier_id:
        return jsonify({'success': False, 'message': '❌ لم يتم العثور على معرف المورد، يرجى إعادة تسجيل الدخول.'}, 400)
    
    try:
        req_data = request.get_json(silent=True) or {}
        page_num = int(req_data.get('page', 1))

        print(f"🔄 [Sync] جاري مزامنة الصفحة {page_num} للمورد: {supplier_id}")

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
        updated_count = 0

        for product in page_products:
            if not isinstance(product, dict):
                continue
            
            qid = product.get('qid') or product.get('id')
            if not qid:
                continue

            with db.session.no_autoflush:
                existing_mapping = ProductSupplierMapping.query.filter_by(product_qid=str(qid)).first()
            
            # إذا لم يكن هناك ارتباط سابق، نتجاهله تماماً ولا نقوم بإنشائه تلقائياً لمنع عودة المنتجات المحذوفة
            if not existing_mapping:
                continue

            if not is_admin and str(existing_mapping.supplier_id) != str(supplier_id):
                continue
            
            synced_count += 1
            updated_count += 1

        db.session.commit()

        has_next = page_num < total_pages

        return jsonify({
            'success': True,
            'message': 'تمت المزامنة بنجاح دون إنشاء ارتباطات عشوائية',
            'syncedCount': synced_count,
            'createdCount': 0,
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
        }, 500)
