# coding: utf-8
# 📂 apps/suppliers_product/edit_product_routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort, jsonify
from flask_login import login_required, current_user
from apps.suppliers_product.sync_edit_product import edit_sync
import logging

logger = logging.getLogger(__name__)

# ✅ تعريف Blueprint
edit_product_bp = Blueprint(
    'edit_product_bp',
    __name__,
    template_folder='templates'
)


# ============================================================
# 🟣 مسار عرض صفحة تعديل المنتج
# ============================================================

@edit_product_bp.route('/edit-product/<qid>', methods=['GET'])
@login_required
def edit_product_page(qid):
    """عرض صفحة تعديل المنتج"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id

        # جلب بيانات المنتج
        result = edit_sync.get_product(qid, supplier_id)

        if not result['success']:
            flash(f'❌ {result["error"]}', 'danger')
            return redirect(url_for('suppliers_product_bp.products'))

        return render_template(
            'suppliers/edit_product.html',
            product=result['product'],
            mapping=result['mapping'],
            supplier=result['supplier']
        )

    except Exception as e:
        logger.error(f"❌ خطأ في edit_product_page: {e}")
        flash('❌ حدث خطأ في تحميل صفحة التعديل', 'danger')
        return redirect(url_for('suppliers_product_bp.products'))


# ============================================================
# 🟣 مسار تحديث المنتج (POST - نموذج)
# ============================================================

@edit_product_bp.route('/edit-product/<qid>', methods=['POST'])
@login_required
def update_product(qid):
    """تحديث بيانات المنتج"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id

        # تجهيز البيانات
        data = {
            'title': request.form.get('title', '').strip(),
            'description': request.form.get('description', '').strip(),
            'price': request.form.get('price', '').strip(),
            'quantity': request.form.get('quantity', '').strip(),
            'status': request.form.get('status', 'DRAFT'),
            'sku': request.form.get('sku', '').strip(),
            'weight': request.form.get('weight', '').strip(),
        }

        # معالجة الصورة
        image = request.files.get('image')
        if image and image.filename:
            data['image_file'] = image.read()
            data['image_filename'] = image.filename

        # تحديث المنتج
        result = edit_sync.update_product(qid, supplier_id, data)

        if result['success']:
            flash('✅ تم تحديث المنتج بنجاح', 'success')
        else:
            flash(f'❌ {result["error"]}', 'danger')

        return redirect(url_for('suppliers_product_bp.products'))

    except Exception as e:
        logger.error(f"❌ خطأ في update_product: {e}")
        flash('❌ حدث خطأ أثناء تحديث المنتج', 'danger')
        return redirect(url_for('edit_product_bp.edit_product_page', qid=qid))


# ============================================================
# 🟣 API: تحديث المنتج (AJAX)
# ============================================================

@edit_product_bp.route('/api/edit-product/<qid>', methods=['PUT'])
@login_required
def api_update_product(qid):
    """API لتحديث المنتج"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id

        result = edit_sync.update_product(qid, supplier_id, request.get_json() or {})

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"❌ خطأ في api_update_product: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 API: تحديث حالة المنتج (AJAX)
# ============================================================

@edit_product_bp.route('/api/edit-product/<qid>/status', methods=['PATCH'])
@login_required
def api_update_status(qid):
    """API لتحديث حالة المنتج"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id
        status = request.get_json().get('status')

        if not status:
            return jsonify({'success': False, 'message': 'الحالة مطلوبة'}), 400

        result = edit_sync.update_product_status(qid, supplier_id, status)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"❌ خطأ في api_update_status: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 API: رفع صورة (AJAX)
# ============================================================

@edit_product_bp.route('/api/edit-product/<qid>/image', methods=['POST'])
@login_required
def api_upload_image(qid):
    """API لرفع صورة للمنتج"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id

        # التحقق من الصلاحية
        if not edit_sync.verify_access(qid, supplier_id):
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'لا توجد صورة'}), 400

        file = request.files['image']
        if not file or not file.filename:
            return jsonify({'success': False, 'message': 'ملف غير صالح'}), 400

        result = edit_sync.add_product_image(qid, file.read(), file.filename)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"❌ خطأ في api_upload_image: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 API: حذف صورة (AJAX)
# ============================================================

@edit_product_bp.route('/api/edit-product/<qid>/image/<image_id>', methods=['DELETE'])
@login_required
def api_remove_image(qid, image_id):
    """API لحذف صورة من المنتج"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id

        # التحقق من الصلاحية
        if not edit_sync.verify_access(qid, supplier_id):
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        result = edit_sync.remove_product_image(qid, image_id)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"❌ خطأ في api_remove_image: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 API: جلب بيانات المنتج (AJAX)
# ============================================================

@edit_product_bp.route('/api/product/<qid>', methods=['GET'])
@login_required
def api_get_product(qid):
    """API لجلب بيانات المنتج"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id

        result = edit_sync.get_product(qid, supplier_id)

        if result['success']:
            return jsonify({'success': True, 'data': result['product']})
        else:
            return jsonify({'success': False, 'message': result['error']}), 404

    except Exception as e:
        logger.error(f"❌ خطأ في api_get_product: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 API: التحقق من SKU (AJAX)
# ============================================================

@edit_product_bp.route('/api/check-sku', methods=['POST'])
@login_required
def api_check_sku():
    """API للتحقق من توفر SKU"""
    try:
        data = request.get_json()
        sku = data.get('sku')
        exclude_qid = data.get('exclude_qid')

        if not sku:
            return jsonify({'success': False, 'message': 'SKU مطلوب'}), 400

        result = edit_sync.check_sku_availability(sku, exclude_qid)

        return jsonify({'success': True, 'data': result})

    except Exception as e:
        logger.error(f"❌ خطأ في api_check_sku: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 API: توليد SKU (AJAX)
# ============================================================

@edit_product_bp.route('/api/generate-sku', methods=['POST'])
@login_required
def api_generate_sku():
    """API لإنشاء SKU تلقائي"""
    try:
        data = request.get_json()
        prefix = data.get('prefix', 'PRD')

        sku = edit_sync.generate_sku(prefix)

        return jsonify({'success': True, 'data': {'sku': sku}})

    except Exception as e:
        logger.error(f"❌ خطأ في api_generate_sku: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
