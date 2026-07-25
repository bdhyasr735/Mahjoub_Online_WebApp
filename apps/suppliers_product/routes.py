# coding: utf-8
# 📂 apps/suppliers_product/routes.py

from flask import Blueprint, render_template, request, session, abort, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from apps.suppliers_product.services import supplier_product, get_product_stats
from apps.suppliers_product.helpers import paginate, filter_by_search, filter_by_status
import logging

logger = logging.getLogger(__name__)

# ====== BLUEPRINTS ======
bp = Blueprint('suppliers_product_bp', __name__, template_folder='templates')
add_bp = Blueprint('add_product_bp', __name__, template_folder='templates')
edit_bp = Blueprint('edit_product_bp', __name__, template_folder='templates')


def _get_supplier_id():
    return current_user.supplier_id if session.get('user_type') == 'staff' else current_user.id


def _check_access():
    if session.get('user_type') not in ['supplier', 'staff']:
        abort(403)


def _render_error(message='حدث خطأ', route='suppliers_product_bp.products'):
    flash(message, 'danger')
    return redirect(url_for(route))


# ============================================
# 📦 قائمة المنتجات
# ============================================

@bp.route('/products')
@login_required
def products():
    _check_access()
    try:
        supplier_id = _get_supplier_id()
        search = request.args.get('search', '').strip()
        filter_status = request.args.get('filter', 'all')
        page = request.args.get('page', 1, type=int)
        
        products_list = []
        for m in supplier_product.get_supplier_mappings(supplier_id):
            p = supplier_product.fetch_product_by_qid(m['qid'])
            if p:
                products_list.append({
                    'qid': m['qid'], 
                    'title': p.get('name') or p.get('title') or 'منتج بدون اسم', 
                    'product': p, 
                    'mapping': m
                })
        
        products_list = filter_by_search(products_list, search, 'title')
        if filter_status != 'all':
            products_list = filter_by_status(products_list, filter_status)
        
        paginated = paginate(products_list, page)
        stats = get_product_stats(supplier_id)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template('suppliers/includes/_table_products.html', products=paginated, pagination=paginated)
        
        return render_template('suppliers/suppliers_product.html',
            products=paginated, pagination=paginated, suppliers=supplier_product.get_active_suppliers(),
            total_products=stats['total'], active_products=stats['published'],
            draft_products=stats['draft'], total_suppliers=len(supplier_product.get_active_suppliers()),
            search_query=search, filter_status=filter_status
        )
    except Exception as e:
        logger.error(f"❌ products: {e}")
        return render_template('suppliers/suppliers_product.html', products={'items': [], 'total': 0})


# ============================================
# ➕ إضافة منتج
# ============================================

@add_bp.route('/add-product', methods=['GET'])
@login_required
def add_product_page():
    _check_access()
    return render_template('suppliers/add_product.html', suppliers=supplier_product.get_active_suppliers())


@add_bp.route('/api/add-product', methods=['POST'])
@login_required
def api_add_product():
    _check_access()
    try:
        data = {k: request.form.get(k, '').strip() for k in ['title', 'description', 'price', 'status', 'sku', 'weight', 'quantity']}
        if not data['title']:
            return jsonify({'success': False, 'message': 'اسم المنتج مطلوب'}), 400
        
        image = request.files.get('image')
        if image and image.filename:
            data['image_file'] = image.read()
            data['image_filename'] = image.filename
        
        result = supplier_product.create_product(_get_supplier_id(), data)
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        logger.error(f"❌ api_add_product: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# ✏️ تعديل منتج
# ============================================

@edit_bp.route('/edit-product/<qid>', methods=['GET'])
@login_required
def edit_product_page(qid):
    _check_access()
    try:
        result = supplier_product.get_product(qid, _get_supplier_id())
        if not result['success']:
            return _render_error(result.get('error', 'المنتج غير موجود'))
        return render_template('suppliers/edit_product.html', product=result['product'], mapping=result['mapping'])
    except Exception as e:
        logger.error(f"❌ edit_product_page: {e}")
        return _render_error('❌ حدث خطأ')


@edit_bp.route('/api/edit-product/<qid>', methods=['PUT'])
@login_required
def api_update_product(qid):
    _check_access()
    try:
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = {k: request.form.get(k, '').strip() for k in ['title', 'description', 'price', 'status', 'sku', 'weight', 'quantity']}
            image = request.files.get('image')
            if image and image.filename:
                data['image_file'] = image.read()
                data['image_filename'] = image.filename
        else:
            data = request.get_json() or {}
        
        result = supplier_product.update_product(qid, _get_supplier_id(), data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"❌ api_update_product: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@edit_bp.route('/api/edit-product/<qid>/status', methods=['PATCH'])
@login_required
def api_update_status(qid):
    _check_access()
    try:
        req_data = request.get_json() or {}
        status = req_data.get('status')
        if not status:
            return jsonify({'success': False, 'message': 'الحالة مطلوبة'}), 400
        result = supplier_product.update_product_status(qid, _get_supplier_id(), status)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"❌ api_update_status: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@edit_bp.route('/api/product/<qid>', methods=['DELETE'])
@login_required
def api_delete_product(qid):
    _check_access()
    try:
        if not supplier_product.verify_access(qid, _get_supplier_id()):
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        result = supplier_product.delete_product(qid, _get_supplier_id())
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"❌ api_delete_product: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# 🖼️ الصور
# ============================================

@edit_bp.route('/api/edit-product/<qid>/image', methods=['POST'])
@login_required
def api_upload_image(qid):
    _check_access()
    try:
        if not supplier_product.verify_access(qid, _get_supplier_id()):
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'لا توجد صورة'}), 400
        file = request.files['image']
        if not file or not file.filename:
            return jsonify({'success': False, 'message': 'ملف غير صالح'}), 400
        result = supplier_product.add_product_image(qid, file.read(), file.filename)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"❌ api_upload_image: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@edit_bp.route('/api/edit-product/<qid>/image/<image_id>', methods=['DELETE'])
@login_required
def api_remove_image(qid, image_id):
    _check_access()
    try:
        if not supplier_product.verify_access(qid, _get_supplier_id()):
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        result = supplier_product.remove_product_image(qid, image_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"❌ api_remove_image: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# 🔍 SKU
# ============================================

@add_bp.route('/api/check-sku', methods=['POST'])
@login_required
def api_check_sku():
    try:
        req_data = request.get_json() or {}
        sku = req_data.get('sku', '').strip()
        if not sku:
            return jsonify({'success': False, 'message': 'SKU مطلوب'}), 400
        result = supplier_product.check_sku_availability(sku)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        logger.error(f"❌ api_check_sku: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@add_bp.route('/api/generate-sku', methods=['POST'])
@login_required
def api_generate_sku():
    try:
        req_data = request.get_json() or {}
        prefix = req_data.get('prefix', 'PRD')
        sku = supplier_product.generate_sku(prefix)
        return jsonify({'success': True, 'data': {'sku': sku}})
    except Exception as e:
        logger.error(f"❌ api_generate_sku: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
