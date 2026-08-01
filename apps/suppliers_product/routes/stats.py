# coding: utf-8
# 📂 apps/suppliers_product/routes/stats.py
# إحصائيات وأرقام الموردين

from flask import render_template, jsonify, redirect, url_for, flash, session
from flask_login import login_required, current_user
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier

@suppliers_product_bp.route('/stats', methods=['GET'])
@login_required
def supplier_stats():
    """صفحة إحصائيات المورد - تعرض ملخص الأداء والمنتجات لحظياً"""
    try:
        supplier_id = getattr(current_user, 'id', None) or session.get('supplier_id') or session.get('user_id') or session.get('_user_id')
        user_type = getattr(current_user, 'user_type', None) or getattr(current_user, 'role', None) or session.get('user_type')
        is_admin = (user_type == 'admin' or getattr(current_user, 'is_admin', False))

        if user_type not in ('supplier', 'admin') and not is_admin:
            flash('❌ هذا القسم مخصص للموردين والمشرفين فقط', 'danger')
            return redirect(url_for('suppliers_dashboard_bp.dashboard'))
        
        supplier_qids_set = set()
        if not is_admin and supplier_id:
            mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
            supplier_qids_set = {str(m.product_qid).strip() for m in mappings if m.product_qid}

        target_products = []
        max_check_pages = 30
        
        for p_num in range(1, max_check_pages + 1):
            res = services.products.get_products_page(p_num)
            if not res or not res.get('data'):
                break
            
            page_items = res.get('data', [])
            for p in page_items:
                p_qid = str(p.get('qid') or p.get('id', '')).strip()
                if not is_admin:
                    if p_qid in supplier_qids_set:
                        target_products.append(p)
                else:
                    target_products.append(p)
            
            if not is_admin and len(target_products) >= len(supplier_qids_set):
                break

        total_products = len(target_products)
        published_count = len([p for p in target_products if str(p.get('status', '')).upper() == 'PUBLISHED'])
        draft_count = len([p for p in target_products if str(p.get('status', '')).upper() == 'DRAFT'])
        rejected_count = len([p for p in target_products if str(p.get('status', '')).upper() == 'REJECTED'])
        
        stats_data = {
            'total_products': total_products,
            'published_count': published_count,
            'draft_count': draft_count,
            'rejected_count': rejected_count
        }

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'stats': stats_data
            })

        return render_template(
            'suppliers/supplier_stats.html',
            stats=stats_data
        )
        
    except Exception as e:
        print(f"❌ خطأ في supplier_stats: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 500
        flash('❌ حدث خطأ في تحميل صفحة الإحصائيات', 'danger')
        return redirect(url_for('suppliers_product_bp.list_supplier_products'))
