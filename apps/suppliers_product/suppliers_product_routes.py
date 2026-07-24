# coding: utf-8
# 📂 apps/suppliers_product/suppliers_product_routes.py

from flask import Blueprint, render_template, request, session, abort, jsonify
from flask_login import login_required, current_user
from apps.suppliers_product import sync_suppliers_product as service
from apps.models.supplier import Supplier
import logging

logger = logging.getLogger(__name__)

# ✅ تعريف Blueprint
suppliers_product_bp = Blueprint(
    'suppliers_product_bp',
    __name__,
    template_folder='templates'
)


# ============================================================
# 🟣 الصفحة الرئيسية - عرض منتجات المورد
# ============================================================

@suppliers_product_bp.route('/products', methods=['GET'])
@login_required
def products():
    """عرض قائمة منتجات المورد"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id

        # ✅ جلب المعاملات من الطلب
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        search_query = request.args.get('search', '').strip()
        status_filter = request.args.get('status', '').strip()
        supplier_filter = request.args.get('supplier_id', type=int)

        # ✅ جلب قائمة الموردين للفلترة
        suppliers = service.get_suppliers_list()

        # ✅ جلب منتجات المورد
        products = service.get_products(supplier_id, search_query)

        # ✅ فلترة حسب الحالة
        if status_filter:
            products = service.filter_products(products, status=status_filter)

        # ✅ فلترة حسب المورد (للمستخدمين من نوع staff)
        if user_type == 'staff' and supplier_filter:
            products = [p for p in products if p.get('supplier_id') == supplier_filter]

        # ✅ جلب الإحصائيات
        stats = service.get_product_stats(supplier_id)

        # ✅ ترقيم الصفحات
        paginated = service.paginate_products(products, page, limit)

        # ✅ التحقق من طلب AJAX (للبحث)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template(
                'suppliers/includes/_table_products.html',
                products=paginated
            )

        return render_template(
            'suppliers/suppliers_product.html',
            products=paginated,
            suppliers=suppliers,
            total_products=stats.get('total', 0),
            active_products=stats.get('active', 0),
            draft_products=stats.get('draft', 0),
            total_suppliers=len(suppliers),
            search_query=search_query,
            selected_status=status_filter,
            selected_supplier=supplier_filter,
            current_page=page,
            limit=limit
        )

    except Exception as e:
        logger.error(f"❌ خطأ في products: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template(
                'suppliers/includes/_table_products.html',
                products={'items': [], 'total': 0, 'page': 1, 'limit': 20, 'total_pages': 1}
            )

        return render_template(
            'suppliers/suppliers_product.html',
            products={'items': [], 'total': 0, 'page': 1, 'limit': 20, 'total_pages': 1},
            suppliers=[],
            total_products=0,
            active_products=0,
            draft_products=0,
            total_suppliers=0,
            search_query='',
            selected_status='',
            selected_supplier=None,
            current_page=1,
            limit=20
        )


# ============================================================
# 🟣 API: جلب إحصائيات المنتجات (AJAX)
# ============================================================

@suppliers_product_bp.route('/api/products/stats', methods=['GET'])
@login_required
def api_products_stats():
    """API لجلب إحصائيات منتجات المورد"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id

        stats = service.get_product_stats(supplier_id)

        return jsonify({
            'success': True,
            'data': stats
        })

    except Exception as e:
        logger.error(f"❌ خطأ في api_products_stats: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 API: بحث عن المنتجات (AJAX)
# ============================================================

@suppliers_product_bp.route('/api/products/search', methods=['GET'])
@login_required
def api_products_search():
    """API للبحث عن المنتجات"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id
        query = request.args.get('q', '').strip()

        products = service.get_products(supplier_id, query)

        # ✅ تجهيز البيانات للـ API
        results = []
        for item in products:
            product = item.get('product', {})
            results.append({
                'qid': item.get('qid'),
                'title': product.get('title'),
                'price': product.get('price'),
                'status': product.get('status'),
                'image': product.get('images', [{}])[0].get('fileUrl') if product.get('images') else None,
                'supplier_name': item.get('supplier_name')
            })

        return jsonify({
            'success': True,
            'data': results,
            'total': len(results)
        })

    except Exception as e:
        logger.error(f"❌ خطأ في api_products_search: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 API: جلب منتج محدد (AJAX)
# ============================================================

@suppliers_product_bp.route('/api/product/<qid>', methods=['GET'])
@login_required
def api_get_product(qid):
    """API لجلب بيانات منتج محدد"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id

        result = service.get_product_with_mapping(qid, supplier_id)

        if result.get('success'):
            return jsonify({
                'success': True,
                'data': {
                    'product': result.get('product'),
                    'mapping': result.get('mapping')
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('error', 'المنتج غير موجود')
            }), 404

    except Exception as e:
        logger.error(f"❌ خطأ في api_get_product: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 API: تحديث حالة المنتج (AJAX)
# ============================================================

@suppliers_product_bp.route('/api/product/<qid>/status', methods=['PATCH'])
@login_required
def api_update_product_status(qid):
    """API لتحديث حالة المنتج"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id

        data = request.get_json()
        status = data.get('status')

        if not status:
            return jsonify({'success': False, 'message': 'الحالة مطلوبة'}), 400

        # ✅ التحقق من أن المنتج يخص المورد
        if not service.verify_access(qid, supplier_id):
            return jsonify({'success': False, 'message': 'المنتج غير موجود أو غير مصرح'}), 404

        # ✅ تحديث الحالة عبر الواجهة
        result = service.update_product_status(qid, supplier_id, status)

        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result.get('message')
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('error', 'فشل تحديث حالة المنتج')
            }), 400

    except Exception as e:
        logger.error(f"❌ خطأ في api_update_product_status: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 API: حذف منتج (AJAX)
# ============================================================

@suppliers_product_bp.route('/api/product/<qid>', methods=['DELETE'])
@login_required
def api_delete_product(qid):
    """API لحذف منتج"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id

        result = service.delete_product(qid, supplier_id)

        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result.get('message')
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', 'فشل حذف المنتج')
            }), 400

    except Exception as e:
        logger.error(f"❌ خطأ في api_delete_product: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 API: حذف منتجات متعددة (AJAX)
# ============================================================

@suppliers_product_bp.route('/api/products/bulk-delete', methods=['POST'])
@login_required
def api_bulk_delete_products():
    """API لحذف منتجات متعددة"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id

        data = request.get_json()
        qids = data.get('qids', [])

        if not qids:
            return jsonify({'success': False, 'message': 'لا توجد منتجات للحذف'}), 400

        result = service.bulk_delete_products(qids, supplier_id)

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ خطأ في api_bulk_delete_products: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 API: تحديث حالة منتجات متعددة (AJAX)
# ============================================================

@suppliers_product_bp.route('/api/products/bulk-status', methods=['POST'])
@login_required
def api_bulk_update_status():
    """API لتحديث حالة منتجات متعددة"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id

        data = request.get_json()
        qids = data.get('qids', [])
        status = data.get('status')

        if not qids:
            return jsonify({'success': False, 'message': 'لا توجد منتجات للتحديث'}), 400

        if not status:
            return jsonify({'success': False, 'message': 'الحالة مطلوبة'}), 400

        result = service.bulk_update_status(qids, supplier_id, status)

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ خطأ في api_bulk_update_status: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 🟣 API: جلب قائمة الموردين (للمستخدمين من نوع staff)
# ============================================================

@suppliers_product_bp.route('/api/suppliers', methods=['GET'])
@login_required
def api_get_suppliers():
    """API لجلب قائمة الموردين (للمستخدمين من نوع staff)"""
    try:
        user_type = session.get('user_type')
        if user_type != 'staff':
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        suppliers = service.get_suppliers_list()

        return jsonify({
            'success': True,
            'data': suppliers
        })

    except Exception as e:
        logger.error(f"❌ خطأ في api_get_suppliers: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
