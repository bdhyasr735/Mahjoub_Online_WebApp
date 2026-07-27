# coding: utf-8
# 📂 apps/admin_Product/routes/reviews.py
# مراجعة المنتجات

from flask import render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required
from apps.admin_Product.routes import admin_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier
from apps.extensions import db
from datetime import datetime


@admin_product_bp.route('/products/review', methods=['GET'])
@login_required
def review_products():
    """صفحة مراجعة المنتجات - تعرض المنتجات التي حالتها DRAFT"""
    try:
        user_type = session.get('user_type')
        if user_type != 'admin':
            flash('❌ هذا القسم مخصص للإدارة فقط', 'danger')
            return redirect(url_for('admin_dashboard_bp.dashboard'))
        
        # ✅ جلب المنتجات من GraphQL (النتيجة الآن dict)
        result = services.products.get_all_products() or {}
        all_products = result.get('data', [])
        
        # ✅ تصفية المنتجات بحالة DRAFT
        draft_products = [p for p in all_products if p.get('status', '').upper() == 'DRAFT']
        
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
        
        total_draft = len(draft_products)
        total_published = len([p for p in all_products if p.get('status', '').upper() == 'PUBLISHED'])
        total_rejected = len([p for p in all_products if p.get('status', '').upper() == 'REJECTED'])
        
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
        return redirect(url_for('admin_product_bp.manage_products_view'))


@admin_product_bp.route('/products/change-status/<qid>', methods=['POST'])
@login_required
def change_product_status(qid):
    """تغيير حالة المنتج (موافقة/رفض/إعادة للمراجعة)"""
    try:
        user_type = session.get('user_type')
        if user_type != 'admin':
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
        data = request.get_json() or {}
        new_status = data.get('status', '').upper()
        
        valid_statuses = ['PUBLISHED', 'REJECTED', 'DRAFT', 'ARCHIVED']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': 'حالة غير صالحة'}), 400
        
        result = services.products.update_product_data({"qid": qid, "status": new_status})
        
        if result:
            mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
            if mapping:
                mapping.updated_at = datetime.utcnow()
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
            return jsonify({'success': False, 'message': '❌ فشل تغيير الحالة في السيرفر'}), 500
            
    except Exception as e:
        print(f"❌ خطأ في change_product_status: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
