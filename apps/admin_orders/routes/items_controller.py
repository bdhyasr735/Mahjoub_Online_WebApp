# coding: utf-8
# 📂 apps/admin_orders/routes/items_controller.py

from flask import Blueprint, jsonify, request
from flask_login import login_required
from apps.extensions import db
from apps.models.order_items_db import OrderItem

# ✅ تعريف البلوبرينت بـ items_bp ليتمكن registry.py من استيراده
items_bp = Blueprint('items_bp', __name__, url_prefix='/admin/orders/items')

@items_bp.route('', methods=['GET'])
@login_required
def list_items():
    """مسار التحكم بعناصر الطلبات والمنتجات المرتبطة والموردين"""
    try:
        items = OrderItem.query.limit(50).all()
        return jsonify({
            'success': True,
            'count': len(items)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
