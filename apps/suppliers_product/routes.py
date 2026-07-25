# coding: utf-8
# 📂 apps/suppliers_product/routes.py

from flask import Blueprint, render_template, request, session, abort, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from apps.suppliers_product.services import (
    get_supplier_mappings, fetch_product_by_qid, get_active_suppliers,
    get_product, verify_access, create_product, update_product,
    update_product_status, delete_product, get_product_stats
)
from apps.suppliers_product.helpers import paginate, filter_by_search, filter_by_status
import logging

logger = logging.getLogger(__name__)

# ====== BLUEPRINTS ======
bp = Blueprint('suppliers_product_bp', __name__, template_folder='templates')
add_bp = Blueprint('add_product_bp', __name__, template_folder='templates')
edit_bp = Blueprint('edit_product_bp', __name__, template_folder='templates')


# ====== دوال مساعدة ======
def get_supplier_id():
    """الحصول على ID المورد الحالي"""
    return current_user.supplier_id if session.get('user_type') == 'staff' else current_user.id


def check_access():
    """التحقق من صلاحيات المورد"""
    if session.get('user_type') not in ['supplier', 'staff']:
        abort(403)


# ============================================
# 📦 قائمة المنتجات
# ============================================

@bp.route('/products')
@login_required
def products():
    check_access()
    
    try:
        supplier_id = get_supplier_id()
        search = request.args.get('search', '').strip()
        filter_status = request.args.get('filter', 'all')
        page = request.args.get('page', 1, type=int)
        
        # جلب المنتجات
        products = []
        for m in get_supplier_mappings(supplier_id):
            p = fetch_product_by_qid(m['qid'])
            if p:
                products.append({
                    'qid': m['qid'],
                    'title': p.get('name') or p.get('title') or 'منتج بدون اسم',
                    'product': p,
                    'mapping': m
                })
        
        # فلترة وترقيم
        products = filter_by_search(products, search, 'title')
        if filter_status != 'all':
            products = filter_by_status(products, filter_status)
        
        paginated = paginate(products, page)
        stats = get_product_stats(supplier_id)
        
        # AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template('suppliers/includes/_table_products.html', 
                                 products=paginated, pagination=paginated)
        
        return render_template('suppliers/suppliers_product.html',
            products=paginated, pagination=paginated,
            suppliers=get_active_suppliers(),
            total_products=stats['total'],
            active_products=stats['published'],
            draft_products=stats['draft'],
            total_suppliers=len(get_active_suppliers()),
            search_query=search, filter_status=filter_status
        )
    except Exception as e:
        logger.error(f"❌ products: {e}")
        return render_template('suppliers/suppliers_product.html', 
                             products={'items': [], 'total': 0})


# ============================================
# ➕ إضافة منتج
# ============================================

@add_bp.route('/add-product', methods=['GET'])
@login_required
def add_product_page():
    check_access()
    return render_template('suppliers/add_product.html', suppliers=get_active_suppliers())


@add_bp.route('/api/add-product', methods=['POST'])
@login_required
def api_add_product():
    check_access()
    
    try:
        data = {
            'title': request.form.get('title', '').strip(),
            'description': request.form.get('description', '').strip(),
            'price': request.form.get('price', '').strip(),
            'status': request.form.get('status', 'DRAFT'),
            'sku': request.form.get('sku', '').strip(),
            'weight': request.form.get('weight', '').strip(),
            'quantity': request.form.get('quantity', '').strip(),
        }
        
        if not data['title']:
            return jsonify({'success': False, 'message': 'اسم المنتج مطلوب'}), 400
        
        image = request.files.get('image')
        if image and image.filename:
            data['image_file'] = image.read()
            data['image_filename'] = image.filename
        
        result = create_product(get_supplier_id(), data)
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
    check_access()
    
    try:
        result = get_product(qid, get_supplier_id())
        if not result['success']:
            flash(result.get('error', 'المنتج غير موجود'), 'danger')
            return redirect(url_for('suppliers_product_bp.products'))
        
        return render_template('suppliers/edit_product.html', 
                             product=result['product'], mapping=result['mapping'])
    except Exception as e:
        logger.error(f"❌ edit_product_page: {e}")
        flash('❌ حدث خطأ', 'danger')
        return redirect(url_for('suppliers_product_bp.products'))


@edit_bp.route('/api/edit-product/<qid>', methods=['PUT'])
@login_required
def api_update_product(qid):
    check_access()
    
    try:
        # معالجة FormData أو JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = {
                'title': request.form.get('title', '').strip(),
                'description': request.form.get('description', '').strip(),
                'price': request.form.get('price', '').strip(),
                'status': request.form.get('status', 'DRAFT'),
                'sku': request.form.get('sku', '').strip(),
                'weight': request.form.get('weight', '').strip(),
                'quantity': request.form.get('quantity', '').strip(),
            }
            image = request.files.get('image')
            if image and image.filename:
                data['image_file'] = image.read()
                data['image_filename'] = image.filename
        else:
            data = request.get_json() or {}
        
        result = update_product(qid, get_supplier_id(), data)
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"❌ api_update_product: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@edit_bp.route('/api/edit-product/<qid>/status', methods=['PATCH'])
@login_required
def api_update_status(qid):
    check_access()
    
    try:
        status = request.get_json().get('status') if request.get_json() else None
        if not status:
            return jsonify({'success': False, 'message': 'الحالة مطلوبة'}), 400
        
        result = update_product_status(qid, get_supplier_id(), status)
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"❌ api_update_status: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@edit_bp.route('/api/product/<qid>', methods=['DELETE'])
@login_required
def api_delete_product(qid):
    check_access()
    
    try:
        if not verify_access(qid, get_supplier_id()):
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
        result = delete_product(qid, get_supplier_id())
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"❌ api_delete_product: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# 🖼️ الصور (API فقط)
# ============================================

@edit_bp.route('/api/edit-product/<qid>/image', methods=['POST'])
@login_required
def api_upload_image(qid):
    check_access()
    
    try:
        if not verify_access(qid, get_supplier_id()):
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'لا توجد صورة'}), 400
        
        file = request.files['image']
        if not file or not file.filename:
            return jsonify({'success': False, 'message': 'ملف غير صالح'}), 400
        
        from apps.suppliers_product.services import add_product_image
        result = add_product_image(qid, file.read(), file.filename)
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"❌ api_upload_image: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@edit_bp.route('/api/edit-product/<qid>/image/<image_id>', methods=['DELETE'])
@login_required
def api_remove_image(qid, image_id):
    check_access()
    
    try:
        if not verify_access(qid, get_supplier_id()):
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
        from apps.suppliers_product.services import remove_product_image
        result = remove_product_image(qid, image_id)
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"❌ api_remove_image: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# 🔍 SKU (API فقط)
# ============================================

@add_bp.route('/api/check-sku', methods=['POST'])
@login_required
def api_check_sku():
    try:
        sku = request.get_json().get('sku', '').strip() if request.get_json() else ''
        if not sku:
            return jsonify({'success': False, 'message': 'SKU مطلوب'}), 400
        
        from apps.suppliers_product.services import check_sku_availability
        result = check_sku_availability(sku)
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        logger.error(f"❌ api_check_sku: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@add_bp.route('/api/generate-sku', methods=['POST'])
@login_required
def api_generate_sku():
    try:
        prefix = request.get_json().get('prefix', 'PRD') if request.get_json() else 'PRD'
        from apps.suppliers_product.services import generate_sku
        sku = generate_sku(prefix)
        return jsonify({'success': True, 'data': {'sku': sku}})
        
    except Exception as e:
        logger.error(f"❌ api_generate_sku: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
