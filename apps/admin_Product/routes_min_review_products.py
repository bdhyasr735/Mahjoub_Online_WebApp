# coding: utf-8
# 📂 apps/admin_Product/routes_review_products.py

import os
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from apps.services.product_sync_service import ProductSyncService
from apps.models.supplier_db import Supplier
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.extensions import db

# ✅ تعريف الـ Blueprint
review_bp = Blueprint(
    'review_bp',
    __name__,
    template_folder='templates'
)

GRAPHQL_TOKEN = os.environ.get('QUMRA_API_KEY', 'YOUR_ADMIN_API_TOKEN')


# ============================================================
# ✅ صفحة مراجعة المنتجات
# ============================================================
@review_bp.route('/products/review', methods=['GET'])
@login_required
def review_products():
    """
    صفحة مراجعة المنتجات - تعرض المنتجات التي حالتها DRAFT (قيد المراجعة)
    """
    try:
        # ✅ التحقق من صلاحيات الإدارة
        user_type = session.get('user_type')
        if user_type != 'admin':
            flash('❌ هذا القسم مخصص للإدارة فقط', 'danger')
            return redirect(url_for('admin_dashboard_bp.dashboard'))
        
        # ✅ جلب المنتجات من قمرة
        client = ProductSyncService(token=GRAPHQL_TOKEN)
        response_data = client.fetch_products(page=1, limit=100)
        all_products = response_data.get("data", [])
        
        # ✅ تصفية المنتجات التي حالتها DRAFT فقط
        draft_products = [p for p in all_products if p.get('status') == 'DRAFT']
        
        # ✅ جلب الموردين لكل منتج
        for product in draft_products:
            mapping = ProductSupplierMapping.query.filter_by(
                product_qid=product.get('qid')
            ).first()
            if mapping:
                supplier = Supplier.query.get(mapping.supplier_id)
                product['supplier_name'] = supplier.trade_name if supplier else 'غير معروف'
                product['supplier_id'] = mapping.supplier_id
            else:
                product['supplier_name'] = 'غير مرتبط'
                product['supplier_id'] = None
        
        # ✅ إحصائيات
        total_draft = len(draft_products)
        total_published = len([p for p in all_products if p.get('status') == 'PUBLISHED'])
        total_rejected = len([p for p in all_products if p.get('status') == 'REJECTED'])
        
        return render_template(
            'admin/admin_review_products.html',
            products=draft_products,
            total_count=total_draft,
            total_published=total_published,
            total_rejected=total_rejected
        )
        
    except Exception as e:
        print(f"❌ خطأ في review_products: {e}")
        flash('❌ حدث خطأ في تحميل صفحة المراجعة', 'danger')
        return redirect(url_for('admin_dashboard_bp.dashboard'))


# ============================================================
# ✅ تغيير حالة المنتج (موافقة/رفض)
# ============================================================
@review_bp.route('/products/change-status/<qid>', methods=['POST'])
@login_required
def change_status(qid):
    """
    تغيير حالة المنتج (موافقة/رفض/إعادة للمراجعة)
    """
    try:
        # ✅ التحقق من صلاحيات الإدارة
        user_type = session.get('user_type')
        if user_type != 'admin':
            return jsonify({
                'success': False,
                'message': 'غير مصرح لك'
            }), 403
        
        # ✅ جلب الحالة الجديدة
        data = request.get_json()
        new_status = data.get('status', '').upper()
        
        # ✅ التحقق من صحة الحالة
        valid_statuses = ['PUBLISHED', 'REJECTED', 'DRAFT', 'ARCHIVED']
        if new_status not in valid_statuses:
            return jsonify({
                'success': False,
                'message': 'حالة غير صالحة'
            }), 400
        
        # ✅ تحديث الحالة في قمرة
        client = ProductSyncService(token=GRAPHQL_TOKEN)
        result = client.update_product_status(qid, new_status)
        
        if result:
            # ✅ تحديث الحالة في قاعدة البيانات المحلية (اختياري)
            mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
            if mapping:
                mapping.status = new_status.lower()
                db.session.commit()
            
            status_names = {
                'PUBLISHED': '✅ تم النشر',
                'REJECTED': '❌ تم الرفض',
                'DRAFT': '⏳ تمت الإعادة للمراجعة',
                'ARCHIVED': '📦 تمت الأرشفة'
            }
            
            return jsonify({
                'success': True,
                'message': status_names.get(new_status, f'تم تغيير الحالة إلى {new_status}'),
                'status': new_status
            })
        else:
            return jsonify({
                'success': False,
                'message': '❌ فشل تغيير الحالة في قمرة'
            }), 500
            
    except Exception as e:
        print(f"❌ خطأ في change_status: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ============================================================
# ✅ حذف المنتج (من صفحة المراجعة)
# ============================================================
@review_bp.route('/products/delete/<qid>', methods=['POST'])
@login_required
def delete_product(qid):
    """
    حذف المنتج من صفحة المراجعة
    """
    try:
        # ✅ التحقق من صلاحيات الإدارة
        user_type = session.get('user_type')
        if user_type != 'admin':
            return jsonify({
                'success': False,
                'message': 'غير مصرح لك'
            }), 403
        
        # ✅ حذف المنتج من قمرة
        client = ProductSyncService(token=GRAPHQL_TOKEN)
        result = client.delete_product(qid)
        
        if result:
            # ✅ حذف الربط من قاعدة البيانات المحلية
            mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
            if mapping:
                db.session.delete(mapping)
                db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '✅ تم حذف المنتج بنجاح'
            })
        else:
            return jsonify({
                'success': False,
                'message': '❌ فشل حذف المنتج'
            }), 500
            
    except Exception as e:
        print(f"❌ خطأ في delete_product: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ============================================================
# ✅ إحصائيات سريعة (AJAX)
# ============================================================
@review_bp.route('/products/stats', methods=['GET'])
@login_required
def get_stats():
    """
    جلب إحصائيات المنتجات للمراجعة (AJAX)
    """
    try:
        user_type = session.get('user_type')
        if user_type != 'admin':
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
        client = ProductSyncService(token=GRAPHQL_TOKEN)
        response_data = client.fetch_products(page=1, limit=100)
        all_products = response_data.get("data", [])
        
        stats = {
            'total': len(all_products),
            'draft': len([p for p in all_products if p.get('status') == 'DRAFT']),
            'published': len([p for p in all_products if p.get('status') == 'PUBLISHED']),
            'rejected': len([p for p in all_products if p.get('status') == 'REJECTED']),
            'archived': len([p for p in all_products if p.get('status') == 'ARCHIVED'])
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
