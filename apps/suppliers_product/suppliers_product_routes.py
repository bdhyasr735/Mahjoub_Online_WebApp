# coding: utf-8
# 📂 apps/suppliers_product/routes/products.py

from flask import Blueprint, render_template, request, session, abort, jsonify
from flask_login import login_required, current_user
from apps.services.product_sync_service import ProductSyncService
from apps.services.product_mapping_service import product_mapping
from apps.models.supplier import Supplier
from apps.extensions import db
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

        # جلب قائمة الموردين للفلترة
        suppliers = Supplier.query.filter_by(status='active').all()

        # جلب المنتجات المرتبطة بالمورد
        mappings = product_mapping.get_all_mappings()
        
        # فلترة حسب المورد
        filtered_mappings = {
            k: v for k, v in mappings.items() 
            if v.get('supplier_id') == supplier_id
        }

        # فلترة حسب البحث
        search_query = request.args.get('search', '').strip()
        if search_query:
            filtered_mappings = {
                k: v for k, v in filtered_mappings.items()
                if search_query.lower() in v.get('product_title', '').lower()
                or search_query.lower() in v.get('qid', '').lower()
            }

        # جلب بيانات المنتجات من قمرة
        sync_service = ProductSyncService()
        products_list = []
        
        for local_id, mapping in filtered_mappings.items():
            qid = mapping.get('qid')
            product_data = sync_service.fetch_product_by_qid(qid) if qid else None
            if product_data:
                products_list.append({
                    'local_id': local_id,
                    'qid': qid,
                    'product': product_data,
                    'supplier_id': mapping.get('supplier_id'),
                    'supplier_name': mapping.get('supplier_name'),
                    'status': mapping.get('status'),
                    'created_at': mapping.get('created_at')
                })

        # إحصائيات
        total_products = len(products_list)
        active_products = sum(1 for p in products_list if p['product'].get('status') == 'ACTIVE' or p['product'].get('status') == 'PUBLISHED')
        draft_products = sum(1 for p in products_list if p['product'].get('status') == 'DRAFT')
        total_suppliers = len(suppliers)

        # التحقق من طلب AJAX (للبحث)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template(
                'suppliers/includes/_table_products.html',
                products={'items': products_list, 'total': total_products}
            )

        return render_template(
            'suppliers/suppliers_product.html',
            products={'items': products_list, 'total': total_products},
            suppliers=suppliers,
            total_products=total_products,
            active_products=active_products,
            draft_products=draft_products,
            total_suppliers=total_suppliers,
            search_query=search_query
        )

    except Exception as e:
        logger.error(f"❌ خطأ في products: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template('suppliers/includes/_table_products.html', products={'items': [], 'total': 0})
        
        return render_template(
            'suppliers/suppliers_product.html',
            products={'items': [], 'total': 0},
            suppliers=[],
            total_products=0,
            active_products=0,
            draft_products=0,
            total_suppliers=0,
            search_query=''
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

        # جلب المنتجات المرتبطة بالمورد
        mappings = product_mapping.get_all_mappings()
        filtered_mappings = {
            k: v for k, v in mappings.items() 
            if v.get('supplier_id') == supplier_id
        }

        sync_service = ProductSyncService()
        total = 0
        active = 0
        draft = 0
        inactive = 0
        archived = 0

        for mapping in filtered_mappings.values():
            qid = mapping.get('qid')
            product_data = sync_service.fetch_product_by_qid(qid) if qid else None
            if product_data:
                total += 1
                status = product_data.get('status', '').upper()
                if status in ['ACTIVE', 'PUBLISHED']:
                    active += 1
                elif status == 'DRAFT':
                    draft += 1
                elif status == 'INACTIVE':
                    inactive += 1
                elif status == 'ARCHIVED':
                    archived += 1

        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'active': active,
                'draft': draft,
                'inactive': inactive,
                'archived': archived
            }
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

        # جلب المنتجات المرتبطة بالمورد
        mappings = product_mapping.get_all_mappings()
        filtered_mappings = {
            k: v for k, v in mappings.items() 
            if v.get('supplier_id') == supplier_id
        }

        # فلترة حسب البحث
        if query:
            filtered_mappings = {
                k: v for k, v in filtered_mappings.items()
                if query.lower() in v.get('product_title', '').lower()
                or query.lower() in v.get('qid', '').lower()
            }

        # جلب بيانات المنتجات
        sync_service = ProductSyncService()
        results = []
        
        for local_id, mapping in filtered_mappings.items():
            qid = mapping.get('qid')
            product_data = sync_service.fetch_product_by_qid(qid) if qid else None
            if product_data:
                results.append({
                    'local_id': local_id,
                    'qid': qid,
                    'title': product_data.get('title'),
                    'price': product_data.get('price'),
                    'status': product_data.get('status'),
                    'image': product_data.get('images', [{}])[0].get('fileUrl') if product_data.get('images') else None
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

        # التحقق من أن المنتج يخص المورد
        mapping = product_mapping.get_mapping_by_qid(qid)
        if not mapping or mapping.get('supplier_id') != supplier_id:
            return jsonify({'success': False, 'message': 'المنتج غير موجود أو غير مصرح'}), 404

        # جلب بيانات المنتج من قمرة
        sync_service = ProductSyncService()
        product_data = sync_service.fetch_product_by_qid(qid)

        if not product_data:
            return jsonify({'success': False, 'message': 'المنتج غير موجود في قمرة'}), 404

        return jsonify({
            'success': True,
            'data': {
                'product': product_data,
                'mapping': mapping
            }
        })

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

        # التحقق من أن المنتج يخص المورد
        mapping = product_mapping.get_mapping_by_qid(qid)
        if not mapping or mapping.get('supplier_id') != supplier_id:
            return jsonify({'success': False, 'message': 'المنتج غير موجود أو غير مصرح'}), 404

        data = request.get_json()
        status = data.get('status')

        if not status:
            return jsonify({'success': False, 'message': 'الحالة مطلوبة'}), 400

        # تحديث حالة المنتج في قمرة
        sync_service = ProductSyncService()
        success = sync_service.update_product_status(qid, status)

        if success:
            # تحديث حالة الربط
            product_mapping.update_mapping_status(qid, status)
            return jsonify({'success': True, 'message': f'تم تحديث الحالة إلى {status}'})
        else:
            return jsonify({'success': False, 'message': 'فشل تحديث حالة المنتج'}), 400

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

        # التحقق من أن المنتج يخص المورد
        mapping = product_mapping.get_mapping_by_qid(qid)
        if not mapping or mapping.get('supplier_id') != supplier_id:
            return jsonify({'success': False, 'message': 'المنتج غير موجود أو غير مصرح'}), 404

        # حذف المنتج من قمرة
        sync_service = ProductSyncService()
        success = sync_service.delete_product(qid, delete_mapping=True)

        if success:
            return jsonify({'success': True, 'message': 'تم حذف المنتج بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'فشل حذف المنتج'}), 400

    except Exception as e:
        logger.error(f"❌ خطأ في api_delete_product: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
