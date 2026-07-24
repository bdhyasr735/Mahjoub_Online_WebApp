# coding: utf-8
# 📂 apps/suppliers_product/routes/add_product.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort, jsonify
from flask_login import login_required, current_user
from apps.suppliers_product.services import add_sync
import logging

logger = logging.getLogger(__name__)

# ✅ تعريف Blueprint
add_product_bp = Blueprint(
    'add_product_bp',
    __name__,
    template_folder='templates'
)


# ============================================================
# 🟣 مسار عرض صفحة إضافة المنتج
# ============================================================

@add_product_bp.route('/add-product', methods=['GET'])
@login_required
def add_product_page():
    """عرض صفحة إضافة منتج جديد"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)

        # جلب قائمة الموردين النشطين
        suppliers = add_sync.get_active_suppliers()

        return render_template(
            'suppliers/add_product.html',
            suppliers=suppliers
        )

    except Exception as e:
        logger.error(f"❌ خطأ في add_product_page: {e}")
        flash('❌ حدث خطأ في تحميل صفحة الإضافة', 'danger')
        return redirect(url_for('suppliers_product_bp.products'))


# ============================================================
# 🟣 مسار إضافة المنتج (POST - نموذج)
# ============================================================

@add_product_bp.route('/api/add-product', methods=['POST'])
@login_required
def api_add_product():
    """
    API لإضافة منتج جديد
    
    البيانات المتوقعة (FormData):
    - title: اسم المنتج (مطلوب)
    - description: وصف المنتج
    - price: السعر
    - status: الحالة (DRAFT, ACTIVE, INACTIVE)
    - supplier_id: معرف المورد (مطلوب)
    - sku: رقم SKU
    - weight: الوزن
    - quantity: الكمية
    - image: ملف الصورة (اختياري)
    """
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        # تحديد supplier_id
        if user_type == 'staff':
            supplier_id = request.form.get('supplier_id', type=int)
            if not supplier_id:
                return jsonify({
                    'success': False,
                    'message': 'معرف المورد مطلوب'
                }), 400
        else:
            supplier_id = current_user.id

        # تجهيز البيانات
        data = {
            'title': request.form.get('title', '').strip(),
            'description': request.form.get('description', '').strip(),
            'price': request.form.get('price', '').strip(),
            'status': request.form.get('status', 'DRAFT'),
            'sku': request.form.get('sku', '').strip(),
            'weight': request.form.get('weight', '').strip(),
            'quantity': request.form.get('quantity', '').strip(),
        }

        # التحقق من البيانات المطلوبة
        if not data['title']:
            return jsonify({
                'success': False,
                'message': 'اسم المنتج مطلوب'
            }), 400

        # معالجة الصورة
        image = request.files.get('image')
        if image and image.filename:
            data['image_file'] = image.read()
            data['image_filename'] = image.filename

        # إنشاء المنتج
        result = add_sync.create_product(supplier_id, data)

        if result['success']:
            return jsonify({
                'success': True,
                'message': 'تم إضافة المنتج بنجاح',
                'data': {
                    'qid': result.get('qid'),
                    'title': data['title']
                }
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': result.get('error', 'فشل إضافة المنتج')
            }), 400

    except Exception as e:
        logger.error(f"❌ خطأ في api_add_product: {e}")
        return jsonify({
            'success': False,
            'message': f'خطأ: {str(e)}'
        }), 500


# ============================================================
# 🟣 API: رفع صورة فقط (AJAX)
# ============================================================

@add_product_bp.route('/api/upload-image', methods=['POST'])
@login_required
def api_upload_image():
    """API لرفع صورة فقط (بدون إنشاء منتج)"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'لا توجد صورة'}), 400

        file = request.files['image']
        if not file or not file.filename:
            return jsonify({'success': False, 'message': 'ملف غير صالح'}), 400

        # رفع الصورة عبر خدمة المزامنة
        from apps.services.product_sync_service import ProductSyncService
        sync_service = ProductSyncService()
        
        image_data = file.read()
        image_url = sync_service.upload_image(image_data, file.filename)

        if image_url:
            return jsonify({
                'success': True,
                'message': 'تم رفع الصورة بنجاح',
                'data': {
                    'url': image_url,
                    'filename': file.filename
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'فشل رفع الصورة'
            }), 400

    except Exception as e:
        logger.error(f"❌ خطأ في api_upload_image: {e}")
        return jsonify({
            'success': False,
            'message': f'خطأ: {str(e)}'
        }), 500


# ============================================================
# 🟣 API: التحقق من SKU (AJAX)
# ============================================================

@add_product_bp.route('/api/check-sku', methods=['POST'])
@login_required
def api_check_sku():
    """API للتحقق من توفر SKU"""
    try:
        data = request.get_json()
        sku = data.get('sku', '').strip()

        if not sku:
            return jsonify({'success': False, 'message': 'SKU مطلوب'}), 400

        result = add_sync.check_sku_availability(sku)

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        logger.error(f"❌ خطأ في api_check_sku: {e}")
        return jsonify({
            'success': False,
            'message': f'خطأ: {str(e)}'
        }), 500


# ============================================================
# 🟣 API: توليد SKU (AJAX)
# ============================================================

@add_product_bp.route('/api/generate-sku', methods=['POST'])
@login_required
def api_generate_sku():
    """API لإنشاء SKU تلقائي"""
    try:
        data = request.get_json() or {}
        prefix = data.get('prefix', 'PRD')

        sku = add_sync.generate_sku(prefix)

        return jsonify({
            'success': True,
            'data': {'sku': sku}
        })

    except Exception as e:
        logger.error(f"❌ خطأ في api_generate_sku: {e}")
        return jsonify({
            'success': False,
            'message': f'خطأ: {str(e)}'
        }), 500


# ============================================================
# 🟣 API: جلب قائمة الموردين (AJAX)
# ============================================================

@add_product_bp.route('/api/suppliers', methods=['GET'])
@login_required
def api_get_suppliers():
    """API لجلب قائمة الموردين النشطين"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        suppliers = add_sync.get_active_suppliers()

        return jsonify({
            'success': True,
            'data': suppliers
        })

    except Exception as e:
        logger.error(f"❌ خطأ في api_get_suppliers: {e}")
        return jsonify({
            'success': False,
            'message': f'خطأ: {str(e)}'
        }), 500
