# coding: utf-8
# 📂 apps/suppliers_product/routes.py

from flask import Blueprint, render_template, request, session, abort, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from apps.suppliers_product.services import supplier_product, get_product_stats
from apps.suppliers_product.helpers import paginate, filter_by_search
import logging

logger = logging.getLogger(__name__)

# ====== BLUEPRINTS ======
suppliers_product_bp = Blueprint('suppliers_product_bp', __name__, template_folder='templates')
add_product_bp = Blueprint('add_product_bp', __name__, template_folder='templates')
edit_product_bp = Blueprint('edit_product_bp', __name__, template_folder='templates')


# ====== PRODUCTS ======
@suppliers_product_bp.route('/products', methods=['GET'])
@login_required
def products():
    """عرض قائمة منتجات المورد"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id
        search = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)

        mappings = supplier_product.get_supplier_mappings(supplier_id)
        products = []
        for m in mappings:
            product = supplier_product.fetch_product_by_qid(m['qid'])
            if product:
                products.append({'qid': m['qid'], 'product': product, 'mapping': m})

        products = filter_by_search(products, search, 'title')
        paginated = paginate(products, page)
        stats = get_product_stats(supplier_id)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template('suppliers/includes/_table_products.html', products=paginated)

        return render_template(
            'suppliers/suppliers_product.html',
            products=paginated,
            suppliers=supplier_product.get_active_suppliers(),
            total_products=stats['total'],
            active_products=stats['published'],
            draft_products=stats['draft'],
            total_suppliers=len(supplier_product.get_active_suppliers()),
            search_query=search
        )
    except Exception as e:
        logger.error(f"❌ خطأ في products: {e}")
        return render_template('suppliers/suppliers_product.html', products={'items': [], 'total': 0})


# ====== ADD PRODUCT ======
@add_product_bp.route('/add-product', methods=['GET'])
@login_required
def add_product_page():
    """صفحة إضافة منتج جديد"""
    try:
        if session.get('user_type') not in ['supplier', 'staff']:
            abort(403)
        return render_template('suppliers/add_product.html', suppliers=supplier_product.get_active_suppliers())
    except Exception as e:
        logger.error(f"❌ خطأ في add_product_page: {e}")
        flash('❌ حدث خطأ في تحميل صفحة الإضافة', 'danger')
        return redirect(url_for('suppliers_product_bp.products'))


@add_product_bp.route('/api/add-product', methods=['POST'])
@login_required
def api_add_product():
    """API إضافة منتج جديد"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        supplier_id = request.form.get('supplier_id', type=int) if user_type == 'staff' else current_user.id
        if not supplier_id:
            return jsonify({'success': False, 'message': 'المورد مطلوب'}), 400

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

        result = supplier_product.create_product(supplier_id, data)
        return jsonify(result), 201 if result['success'] else 400

    except Exception as e:
        logger.error(f"❌ خطأ في api_add_product: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@add_product_bp.route('/api/check-sku', methods=['POST'])
@login_required
def api_check_sku():
    """API التحقق من توفر SKU"""
    try:
        data = request.get_json()
        sku = data.get('sku', '').strip() if data else ''
        if not sku:
            return jsonify({'success': False, 'message': 'SKU مطلوب'}), 400
        result = supplier_product.check_sku_availability(sku)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        logger.error(f"❌ خطأ في api_check_sku: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@add_product_bp.route('/api/generate-sku', methods=['POST'])
@login_required
def api_generate_sku():
    """API توليد SKU تلقائي"""
    try:
        data = request.get_json()
        prefix = data.get('prefix', 'PRD') if data else 'PRD'
        sku = supplier_product.generate_sku(prefix)
        return jsonify({'success': True, 'data': {'sku': sku}})
    except Exception as e:
        logger.error(f"❌ خطأ في api_generate_sku: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ====== EDIT PRODUCT ======
@edit_product_bp.route('/edit-product/<qid>', methods=['GET'])
@login_required
def edit_product_page(qid):
    """صفحة تعديل منتج"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id
        result = supplier_product.get_product(qid, supplier_id)

        if not result['success']:
            flash(result['error'], 'danger')
            return redirect(url_for('suppliers_product_bp.products'))

        return render_template('suppliers/edit_product.html',
            product=result['product'],
            mapping=result['mapping']
        )
    except Exception as e:
        logger.error(f"❌ خطأ في edit_product_page: {e}")
        flash('❌ حدث خطأ في تحميل صفحة التعديل', 'danger')
        return redirect(url_for('suppliers_product_bp.products'))


@edit_product_bp.route('/edit-product/<qid>', methods=['POST'])
@login_required
def update_product(qid):
    """تحديث منتج (نموذج)"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id

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

        result = supplier_product.update_product(qid, supplier_id, data)

        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result.get('error', 'فشل تحديث المنتج'), 'danger')

        return redirect(url_for('suppliers_product_bp.products'))

    except Exception as e:
        logger.error(f"❌ خطأ في update_product: {e}")
        flash('❌ حدث خطأ أثناء تحديث المنتج', 'danger')
        return redirect(url_for('edit_product_bp.edit_product_page', qid=qid))


@edit_product_bp.route('/api/edit-product/<qid>', methods=['PUT'])
@login_required
def api_update_product(qid):
    """API تحديث منتج"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id
        
        # دعم استقبال البيانات سواء كانت عبر FormData أو JSON
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

        result = supplier_product.update_product(qid, supplier_id, data)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"❌ خطأ في api_update_product: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@edit_product_bp.route('/api/edit-product/<qid>/status', methods=['PATCH'])
@login_required
def api_update_status(qid):
    """API تحديث حالة المنتج"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id
        data = request.get_json() or {}
        status = data.get('status')

        if not status:
            return jsonify({'success': False, 'message': 'الحالة مطلوبة'}), 400

        result = supplier_product.update_product_status(qid, supplier_id, status)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"❌ خطأ في api_update_status: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@edit_product_bp.route('/api/edit-product/<qid>/image', methods=['POST'])
@login_required
def api_upload_image(qid):
    """API رفع صورة للمنتج"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id

        if not supplier_product.verify_access(qid, supplier_id):
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'لا توجد صورة'}), 400

        file = request.files['image']
        if not file or not file.filename:
            return jsonify({'success': False, 'message': 'ملف غير صالح'}), 400

        result = supplier_product.add_product_image(qid, file.read(), file.filename)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"❌ خطأ في api_upload_image: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@edit_product_bp.route('/api/edit-product/<qid>/image/<image_id>', methods=['DELETE'])
@login_required
def api_remove_image(qid, image_id):
    """API حذف صورة من المنتج"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id

        if not supplier_product.verify_access(qid, supplier_id):
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        result = supplier_product.remove_product_image(qid, image_id)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"❌ خطأ في api_remove_image: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@edit_product_bp.route('/api/product/<qid>', methods=['DELETE'])
@login_required
def api_delete_product(qid):
    """API حذف منتج"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id

        if not supplier_product.verify_access(qid, supplier_id):
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        result = supplier_product.delete_product(qid, supplier_id)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"❌ خطأ في api_delete_product: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
