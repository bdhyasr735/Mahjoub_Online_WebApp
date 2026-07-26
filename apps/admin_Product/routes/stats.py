# coding: utf-8
# 📂 apps/admin_Product/routes/stats.py
# إحصائيات المنتجات

from flask import jsonify, session
from flask_login import login_required
from apps.admin_Product.routes import admin_product_bp
from apps.services import services


@admin_product_bp.route('/products/stats', methods=['GET'])
@login_required
def get_stats():
    """جلب إحصائيات المنتجات للمراجعة (AJAX)"""
    try:
        user_type = session.get('user_type')
        if user_type != 'admin':
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
        all_products = services.products.get_all_products()
        
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
        return jsonify({'success': False, 'message': str(e)}), 500
