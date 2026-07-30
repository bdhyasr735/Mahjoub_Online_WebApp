# coding: utf-8
# apps/admin_Product/routes/stats.py

from flask import jsonify, session
from flask_login import login_required
from apps.admin_Product.routes import admin_product_bp
from apps.services import services


@admin_product_bp.route('/products/stats', methods=['GET'])
@login_required
def get_stats():
    """جلب إحصائيات المنتجات (تستخدم الحالات الجديدة)"""
    try:
        user_type = session.get('user_type')
        if user_type != 'admin':
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
        result = services.products.get_all_products() or {}
        all_products = result.get('data', [])
        
        # الحالات الجديدة: active, draft, archived
        stats = {
            'total': len(all_products),
            'active': len([p for p in all_products if p.get('status', '').lower() == 'active']),
            'draft': len([p for p in all_products if p.get('status', '').lower() == 'draft']),
            'archived': len([p for p in all_products if p.get('status', '').lower() == 'archived'])
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        print(f"❌ خطأ في get_stats: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
