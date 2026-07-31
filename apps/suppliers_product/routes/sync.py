# coding: utf-8
# apps/suppliers_product/routes/sync.py
# مزامنة منتجات الموردين - مزامنة تدريجية آمنة وذكية

import functools
import math
import traceback
from flask import request, jsonify, session, current_app
from flask_login import login_required
from flask_wtf.csrf import csrf_exempt  # ✅ استيراد مهم
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
@csrf_exempt  # ✅ تم تعطيل CSRF مؤقتاً لتأكيد الخطأ
@analyze_render_error
def sync_supplier_products():
    """مزامنة منتجات المورد بشكل تدريجي وذكي (صفحة صفحة) لتجنب الانهيار"""
    user_type = session.get('user_type')
    supplier_id = session.get('user_id') or session.get('supplier_id')

    if user_type not in ('supplier', 'admin'):
        return jsonify({'success': False, 'message': 'غير مصرح لك بالوصول'}), 403
    
    try:
        from apps.extensions import db

        print(f"🔍 [Sync] بدء المزامنة للمورد {supplier_id}")

        # ✅ 1. جلب جميع QIDs الخاصة بالمورد من قاعدة البيانات المحلية (سريع جداً)
        supplier_qids = []
        if supplier_id:
            mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
            supplier_qids = [m.product_qid for m in mappings]
            print(f"🔍 [Sync] تم جلب {len(supplier_qids)} QID للمورد")

        # إذا لم يكن لدى المورد أي منتجات مرتبطة، ننهي المزامنة فوراً
        if not supplier_qids:
            print(f"⚠️ [Sync] لا توجد منتجات مرتبطة بهذا المورد")
            return jsonify({
                'success': True,
                'message': 'ℹ️ لا توجد منتجات مرتبطة بهذا المورد للمزامنة.',
                'syncedCount': 0,
                'createdCount': 0,
                'updatedCount': 0,
                'errors': []
            })

        supplier_qids_set = set(supplier_qids)

        # ✅ 2. إعداد المتغيرات (نعتمد على عدد الـ QIDs المحلية لحساب الصفحات)
        per_page = 10  # حجم الدفعة
        total_items_real = len(supplier_qids_set)
        total_pages = math.ceil(total_items_real / per_page)

        synced_count = 0
        created_count = 0
        updated_count = 0
        errors = []

        print(f"🔄 [Sync] سيتم جلب {total_pages} صفحة (إجمالي {total_items_real} منتج)")

        # ✅ 3. التكرار عبر الصفحات، ولكن نجلب فقط المنتجات التي تخص هذا المورد
        for page_num in range(1, total_pages + 1):
            print(f"🔄 [Sync] مزامنة الصفحة {page_num}/{total_pages} (للمورد {supplier_id})")
            try:
                # جلب صفحة من GraphQL
                result = services.products.get_products_page(page_num)
                if not result:
                    print(f"⚠️ [Sync] صفحة {page_num} لم تُرجع بيانات")
                    continue
                
                page_products = result.get('data', [])
                print(f"📄 [Sync] الصفحة {page_num} تحتوي على {len(page_products)} منتج")
                
                # تصفية المنتجات: نحتفظ فقط بما هو موجود في مجموعة الـ QIDs المحلية
                for product in page_products:
                    if not isinstance(product, dict):
                        continue
                    qid = product.get('qid')
                    if not qid or qid not in supplier_qids_set:
                        continue
                    
                    # المنتج موجود في قاعدة البيانات المحلية → نقوم بتحديثه أو إنشائه
                    mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
                    
                    synced_count += 1
                    if not mapping:
                        created_count += 1
                        # إنشاء سجل ربط جديد (إذا لم يكن موجوداً)
                        new_mapping = ProductSupplierMapping(product_qid=qid, supplier_id=supplier_id)
                        db.session.add(new_mapping)
                        db.session.commit()
                        print(f"✅ [Sync] إنشاء ربط جديد للمنتج {qid}")
                    else:
                        updated_count += 1
                        # تحديث تاريخ التحديث (سيتم تلقائياً بواسطة onupdate في المودل)
                        db.session.commit()
                        print(f"🔄 [Sync] تحديث ربط المنتج {qid}")

            except Exception as page_error:
                print(f"⚠️ [Sync] خطأ في الصفحة {page_num}: {page_error}")
                errors.append({'page': page_num, 'error': str(page_error)})

        print(f"✅ [Sync] تمت المزامنة بنجاح: {synced_count} منتج")

        # ✅ 4. إرجاع النتيجة النهائية
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
        print(f"❌ [Sync] خطأ غير متوقع في sync_supplier_products: {traceback.format_exc()}")
        return jsonify({
            'success': False, 
            'message': f'❌ فشل المزامنة: {str(e)}',
            'errors': [{'error': str(e)}]
        }), 500
