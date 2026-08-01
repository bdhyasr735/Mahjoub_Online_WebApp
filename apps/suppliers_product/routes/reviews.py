# coding: utf-8
# 📂 apps/suppliers_product/routes/reviews.py
# مراجعة منتجات الموردين

from flask import render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required, current_user
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier
from apps.extensions import db
from datetime import datetime


@suppliers_product_bp.route('/products/review', methods=['GET'])
@login_required
def review_supplier_products():
    """صفحة مراجعة منتجات المورد - تعرض المنتجات الخاصة بالمورد الحالي لحظياً"""
    try:
        # ✅ 1. التحقق الآمن من الهُوية وصلاحيات الدخول
        supplier_id = getattr(current_user, 'id', None) or session.get('supplier_id') or session.get('user_id') or session.get('_user_id')
        user_type = getattr(current_user, 'user_type', None) or getattr(current_user, 'role', None) or session.get('user_type')
        is_admin = (user_type == 'admin' or getattr(current_user, 'is_admin', False))

        if user_type not in ('supplier', 'admin') and not is_admin:
            flash('❌ هذا القسم مخصص للموردين والمشرفين فقط', 'danger')
            return redirect(url_for('suppliers_dashboard_bp.dashboard'))
        
        # ====================================================
        # ✅ 2. جلب الـ QIDs المرتبطة بالمورد من قاعدة البيانات المحلية
        # ====================================================
        supplier_qids_set = set()
        if not is_admin and supplier_id:
            mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
            supplier_qids_set = {str(m.product_qid).strip() for m in mappings if m.product_qid}
            
            if not supplier_qids_set:
                # إذا لم تكن لديه أي منتجات مرتبطة
                return render_template(
                    'suppliers/supplier_review_products.html',
                    products=[],
                    total_count=0,
                    total_published=0,
                    total_rejected=0,
                    no_products_message="عذراً، لا توجد لديك أي منتجات مسجلة للمراجعة حالياً."
                )

        # ====================================================
        # ✅ 3. الجلب اللحظي (Stateless) للمنتجات وتصفيتها
        # ====================================================
        target_products = []
        max_check_pages = 30
        
        for p_num in range(1, max_check_pages + 1):
            res = services.products.get_products_page(p_num)
            if not res or not res.get('data'):
                break
            
            page_items = res.get('data', [])
            for p in page_items:
                p_qid = str(p.get('qid') or p.get('id', '')).strip()
                
                # إذا لم يكن مشرفاً، نتحقق أن المنتج يتبع المورد حصراً
                if not is_admin:
                    if p_qid in supplier_qids_set:
                        target_products.append(p)
                else:
                    target_products.append(p)
            
            # إذا استوفَينا جميع منتجات المورد، نتوقف عن التصفح الخارجي لتسريع الصفحة
            if not is_admin and len(target_products) >= len(supplier_qids_set):
                break

        # ====================================================
        # ✅ 4. تصنيف الحالات (مسودة، منشور، مرفوض)
        # ====================================================
        draft_products = []
        total_published = 0
        total_rejected = 0

        for product in draft_products if False else target_products:
            status = str(product.get('status', '')).upper()
            
            # إثراء بيانات المنتج بمعلومات المورد إذا كان المشرف هو من يتصفح
            p_qid = str(product.get('qid') or product.get('id', '')).strip()
            mapping = ProductSupplierMapping.query.filter_by(product_qid=p_qid).first()
            if mapping:
                supplier = Supplier.query.get(mapping.supplier_id)
                product['supplier_name'] = supplier.trade_name if supplier else 'غير معروف'
                product['supplier_id'] = mapping.supplier_id
            else:
                product['supplier_name'] = 'غير مرتبط'
                product['supplier_id'] = None

            if status == 'DRAFT':
                draft_products.append(product)
            elif status == 'PUBLISHED':
                total_published += 1
            elif status == 'REJECTED':
                total_rejected += 1

        total_draft = len(draft_products)
        
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
        return redirect(url_for('suppliers_product_bp.list_supplier_products'))


@suppliers_product_bp.route('/products/change-status/<qid>', methods=['POST'])
@login_required
def change_supplier_product_status(qid):
    """تغيير حالة منتج المورد (بصلاحيات مقيدة)"""
    try:
        supplier_id = getattr(current_user, 'id', None) or session.get('supplier_id') or session.get('user_id') or session.get('_user_id')
        user_type = getattr(current_user, 'user_type', None) or getattr(current_user, 'role', None) or session.get('user_type')
        is_admin = (user_type == 'admin' or getattr(current_user, 'is_admin', False))

        if user_type not in ('supplier', 'admin') and not is_admin:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
        # التحقق من أن المنتج يخص هذا المورد (إلا إذا كان المشرف هو من يقوم بالعملية)
        mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
        if not is_admin:
            if not mapping or str(mapping.supplier_id) != str(supplier_id):
                return jsonify({'success': False, 'message': 'غير مصرح لك بتعديل هذا المنتج'}), 403
        
        data = request.get_json() or {}
        new_status = data.get('status', '').upper()
        
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
