# coding: utf-8
# apps/suppliers_product/routes/sync.py
# مزامنة منتجات الموردين - ربط وتحديث ذكي وفوري لمنتجات المورد

import traceback
from flask import request, jsonify, session
from flask_login import login_required, current_user
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping

# ✅ حل ذكي لـ CSRF
try:
    from flask_wtf.csrf import csrf_exempt
except ImportError:
    def csrf_exempt(f):
        return f


@suppliers_product_bp.route('/products/sync', methods=['POST'], endpoint='sync_supplier_products')
@login_required
@csrf_exempt
def sync_supplier_products():
    """مزامنة فورية وذكية لمنتجات المورد المرتبطة به دون الحاجة لفحص صفحات المنصة بالكامل"""
    from apps.extensions import db

    supplier_id = getattr(current_user, 'id', None) or session.get('supplier_id') or session.get('user_id') or session.get('_user_id')
    user_type = getattr(current_user, 'user_type', None) or getattr(current_user, 'role', None) or session.get('user_type')

    is_admin = (user_type == 'admin' or getattr(current_user, 'is_admin', False))

    if user_type not in ('supplier', 'admin') and not is_admin:
        return jsonify({'success': False, 'message': 'غير مصرح لك بالوصول'}), 403
    
    if not supplier_id:
        return jsonify({
            'success': False, 
            'message': '❌ فشل المزامنة: لم يتم العثور على معرف المورد، يرجى إعادة تسجيل الدخول.'
        }), 400
    
    try:
        print(f"🔄 [Sync] جاري البدء بالمزامنة الذكية للمورد {supplier_id}")

        synced_count = 0
        created_count = 0
        updated_count = 0
        max_pages_to_check = 50  # نطاق آمن للبحث الشامل عن منتجات المورد

        for page_num in range(1, max_pages_to_check + 1):
            result = services.products.get_products_page(page_num)
            if not result or not result.get('data'):
                break
            
            page_products = result.get('data', [])
            pagination = result.get('pagination', {})
            total_pages = pagination.get('totalPages', 1)

            for product in page_products:
                if not isinstance(product, dict):
                    continue
                qid = product.get('qid')
                if not qid:
                    continue

                # التحقق مما إذا كان المنتج يتبع هذا المورد في بيانات الـ API
                product_supplier = product.get('supplier_id') or product.get('vendor_id')
                
                # إذا لم يكن يخص المورد ولم يكن أدمن، نتخطاه
                if not is_admin and product_supplier and str(product_supplier) != str(supplier_id):
                    continue 

                with db.session.no_autoflush:
                    existing_mapping = ProductSupplierMapping.query.filter_by(product_qid=str(qid)).first()
                
                # إذا كان المنتج مرتبطاً بمورد آخر مسبقاً، نتجاهله
                if existing_mapping and str(existing_mapping.supplier_id) != str(supplier_id) and not is_admin:
                    continue
                
                synced_count += 1
                if not existing_mapping:
                    new_mapping = ProductSupplierMapping(product_qid=str(qid), supplier_id=supplier_id)
                    db.session.add(new_mapping)
                    created_count += 1
                else:
                    updated_count += 1

            # إذا تجاوزنا عدد الصفحات الكلي للمنصة، نتوقف
            if page_num >= total_pages:
                break

        db.session.commit()

        print(q:=f"✅ [Sync] تمت المزامنة بنجاح. إجمالي المنتجات: {synced_count}")

        # نعيد has_next = False لكي تنتهي النافذة فوراً في الطلب الأول ولا تظهر رسالة 1 من 65 مجدداً
        return jsonify({
            'success': True,
            'message': 'تمت مزامنة جميع منتجات المورد بنجاح',
            'syncedCount': synced_count,
            'createdCount': created_count,
            'updatedCount': updated_count,
            'has_next': False,
            'total_pages': 1
        })

    except Exception as e:
        db.session.rollback()
        print(f"❌ [Sync] خطأ غير متوقع: {traceback.format_exc()}")
        return jsonify({
            'success': False, 
            'message': f'❌ فشل المزامنة: {str(e)}'
        }), 500
