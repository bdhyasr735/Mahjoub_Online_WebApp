# coding: utf-8
# 📂 apps/admin_orders/routes/items_controller.py

from flask import Blueprint, request, jsonify, render_template

items_bp = Blueprint('items_bp', __name__)

# مسار تعيين المورد للعنصر
@items_bp.route('/admin/orders/<int:order_id>/item/<int:item_id>/assign-supplier', methods=['POST'])
def assign_supplier(order_id, item_id):
    try:
        data = request.get_json()
        supplier_id = data.get('supplier_id')
        
        if supplier_id == "":
            supplier_id = None
        else:
            supplier_id = int(supplier_id) if supplier_id else None

        # منطق التحديث في قاعدة البيانات هنا...

        return jsonify({
            'success': True,
            'message': 'تم تعيين المورد بنجاح',
            'supplier_name': 'اسم المورد'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
