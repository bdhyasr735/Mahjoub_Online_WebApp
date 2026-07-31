# coding: utf-8
# apps/suppliers_product/routes/sync.py
# مزامنة منتجات الموردين - مزامنة تدريجية ذكية وآمنة صفحة بصفحة

import functools
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
    """مزامنة منتجات المورد تدريجياً (تستقبل الصفحة الحالية وتتم معالجتها لتفادي Timeout)"""
    from apps.extensions import db

    # ✅ الحصول على معرف المستخدم ونوعه بشكل مضمون من current_user أو الـ session
    supplier_id = getattr(current_user, 'id', None) or session.get('supplier_id') or session.get('user_id') or session.get('_user_id')
    user_type = getattr(current_user, 'user_type', None) or getattr(current_user, 'role', None) or session.get('user_type')

    is_admin = (user_type == 'admin' or getattr(current_user, 'is_admin', False))

    if user_type not in ('supplier', 'admin') and not is_admin:
        return jsonify({'success': False, 'message': 'غير مصرح لك بالوصول'}), 403
    
    # ✅ حماية إضافية للتأكد من وجود معرف صالح للمورد أو المستخدم
    if not supplier_id:
        print("❌ [Sync Error]: تعذر معرفة معرف المستخدم أو المورد (supplier_id is None)")
        return jsonify({
            'success': False, 
            'message': '❌ فشل المزامنة: لم يتم العثور على معرف المورد في الجلسة، يرجى إعادة تسجيل الدخول.'
        }), 400
    
    try:
        # ✅ استخدام silent=True لمنع انهيار الخادم إذا كان جسم الطلب فارغاً أو غير مكتمل
        data = request.get_json(silent=True) or {}
        
        # استقبال رقم الصفحة الحالية من الطلب (إذا لم ترسل، نبدأ بالصفحة 1)
        page_num = int(data.get('page', 1))
        
        print(f"🔄 [Sync] جاري معالجة الصفحة {page_num} للمورد {supplier_id}")

        # جلب الصفحة المحددة فقط من GraphQL
        result = services.products.get_products_page(page_num)
        if not result:
            return jsonify({
                'success': True, 
                'message': 'تمت المزامنة بنجاح', 
                'syncedCount': 0, 
                'has_next': False
            })

        pagination = result.get('pagination', {})
        total_items = pagination.get('totalItems', 0)
        total_pages = pagination.get('totalPages', 1)
        
        if total_items == 0:
            return jsonify({
                'success': True, 
                'message': 'لا توجد منتجات للمزامنة', 
                'syncedCount': 0, 
                'has_next': False
            })

        page_products = result.get('data', [])
        synced_count = 0
        created_count = 0
        updated_count = 0

        for product in page_products:
            if not isinstance(product, dict):
                continue
            qid = product.get('qid')
            if not qid:
                continue

            # التحقق مما إذا كان المنتج يتبع هذا المورد حصرياً
            product_supplier = product.get('supplier_id') or product.get('vendor_id')
            
            if not is_admin and product_supplier and str(product_supplier) != str(supplier_id):
                continue  # تخطي المنتجات التي تخص مورداً آخر تماماً

            # ✅ استخدام no_autoflush لمنع حدوث فلاش مبكر يؤدي لخطأ القيود
            with db.session.no_autoflush:
                existing_mapping = ProductSupplierMapping.query.filter_by(product_qid=str(qid)).first()
            
            # إذا كان المنتج مرتبطاً بمورد مختلف مسبقاً (والمستخدم ليس أدمن)، نتجاهله
            if existing_mapping and str(existing_mapping.supplier_id) != str(supplier_id) and not is_admin:
                continue
            
            synced_count += 1
            if not existing_mapping:
                new_mapping = ProductSupplierMapping(product_qid=str(qid), supplier_id=supplier_id)
                db.session.add(new_mapping)
                created_count += 1
            else:
                # تحديث المورد إذا لزم الأمر أو الاحتفاظ بالرابط الحالي
                if is_admin and existing_mapping.supplier_id != supplier_id:
                    existing_mapping.supplier_id = supplier_id
                updated_count += 1

        db.session.commit()

        # معرفة ما إذا كانت هناك صفحات أخرى تالية للمزامنة
        has_next = page_num < total_pages
        next_page = page_num + 1 if has_next else None

        return jsonify({
            'success': True,
            'message': f'تمت مزامنة الصفحة {page_num} من {total_pages}',
            'syncedCount': synced_count,
            'createdCount': created_count,
            'updatedCount': updated_count,
            'has_next': has_next,
            'next_page': next_page,
            'total_pages': total_pages
        })

    except Exception as e:
        db.session.rollback()  # ✅ إرجاع قاعدة البيانات للحالة السليمة عند حدوث استثناء
        print(f"❌ [Sync] خطأ غير متوقع: {traceback.format_exc()}")
        return jsonify({
            'success': False, 
            'message': f'❌ فشل المزامنة: {str(e)}'
        }), 500
