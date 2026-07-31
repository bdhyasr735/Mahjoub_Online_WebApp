# coding: utf-8
# 📂 apps/suppliers_product/routes/reviews.py
# مراجعة منتجات الموردين

from flask import render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier
from apps.extensions import db
from datetime import datetime


@suppliers_product_bp.route('/products/review', methods=['GET'])
@login_required
def review_supplier_products():
    """صفحة مراجعة منتجات المورد - تعرض المنتجات الخاصة بالمورد الحالي"""
    try:
        user_type = session.get('user_type')
        supplier_id = session.get('user_id') or session.get('supplier_id')

        if user_type != 'supplier' and user_type != 'admin':
            flash('❌ هذا القسم مخصص للموردين فقط', 'danger')
            return redirect(url_for('suppliers_dashboard_bp.dashboard'))
        
        # جلب المنتجات عبر الخدمة
        result = services.products.get_all_products() or {}
        all_products = result.get('data', [])
        
        # إذا كان المستخدم مورداً، نقوم بتصفية المنتجات لتقتصر على منتجاته المرتبطة في جدول الربط فقط
        if user_type != 'admin' and supplier_id:
            supplier_mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
            supplier_qids = {m.product_qid for m in supplier_mappings}
            target_products = [p for p in all_products if p.get('qid') in supplier_qids]
        else:
            target_products = all_products

        # تصفية المنتجات بحالة DRAFT للمورد
        draft_products = [p for p in target_products if p.get('status', '').upper() == 'DRAFT']
        
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
        total_published = len([p for p in target_products if p.get('status', '').upper() == 'PUBLISHED'])
        total_rejected = len([p for p in target_products if p.get('status', '').upper() == 'REJECTED'])
        
        # تغليف المنتجات لتتطابق مع توقعات القالب (item.product)
        formatted_products = [{'product': p} for p in draft_products]
        
        return render_template(
            'suppliers/supplier_review_products.html',
            products=formatted_products,
            total_count=total_draft,
            total_published=total_published,
            total_rejected=total_rejected
        )
        
    except Exception as e:
        print(f"❌ خطأ في review_supplier_products: {e}")
        flash('❌ حدث خطأ في تحميل صفحة المراجعة', 'danger')
        return redirect(url_for('suppliers_product_bp.manage_supplier_products'))


@suppliers_product_bp.route('/products/change-status/<qid>', methods=['POST'])
@login_required
def change_supplier_product_status(qid):
    """تغيير حالة منتج المورد (بصلاحيات مقيدة)"""
    try:
        user_type = session.get('user_type')
        supplier_id = session.get('user_id') or session.get('supplier_id')

        if user_type != 'supplier' and user_type != 'admin':
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
        # التحقق من أن المنتج يخص هذا المورد (إلا إذا كان المشرف هو من يقوم بالعملية)
        mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
        if user_type != 'admin':
            if not mapping or str(mapping.supplier_id) != str(supplier_id):
                return jsonify({'success': False, 'message': 'غير مصرح لك بتعديل هذا المنتج'}), 403
        
        data = request.get_json() or {}
        new_status = data.get('status', '').upper()
        
        # المورد قد يكون مسموحاً له حالات محدودة مثل DRAFT أو إعادة إرسال للمراجعة، بينما الإدارة تملك كل الصلاحيات
        valid_statuses = ['PUBLISHED', 'REJECTED', 'DRAFT', 'ARCHIVED']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': 'حالة غير صالحة'}), 400
        
        result = services.products.update_product_data({"qid": qid, "status": new_status})
        
        if result:
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
        print(f"❌ خطأ في change_supplier_product_status: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
