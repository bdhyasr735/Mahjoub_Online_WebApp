# coding: utf-8
# 📂 apps/admin_orders/routes/items_controller.py

from flask import Blueprint, request, jsonify, render_template, current_app

items_bp = Blueprint('items_bp', __name__)

# 1. مسار جلب وعرض عناصر الطلب داخل الجدول (مصحح ليقبل المعرفات النصية)
@items_bp.route('/admin/orders/<string:order_id>/items', methods=['GET'])
def get_order_items(order_id):
    try:
        from apps.models.order_items_db import OrderItem
        from apps.models.supplier_db import Supplier
        
        items_list = OrderItem.query.filter_by(order_id=order_id).all()
        all_suppliers = Supplier.query.all() if hasattr(Supplier, 'query') else []
        
        return render_template(
            'admin/order/_items_table_card.html', 
            items_list=items_list, 
            all_suppliers=all_suppliers,
            order_id=order_id
        )
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        current_app.logger.error(f"❌ [Items Route Error]: {error_msg}")
        return f'<div class="alert alert-danger m-3"><strong>خطأ في تحميل العناصر:</strong><pre dir="ltr">{str(e)}</pre></div>', 500

# 2. مسار تعيين المورد للعنصر (مصحح ليقبل المعرفات النصية)
@items_bp.route('/admin/orders/<string:order_id>/item/<int:item_id>/assign-supplier', methods=['POST'])
def assign_supplier(order_id, item_id):
    try:
        data = request.get_json()
        supplier_id = data.get('supplier_id')
        
        if supplier_id == "" or supplier_id is None:
            supplier_id = None
            supplier_name = "-- بدون مورد --"
        else:
            supplier_id = int(supplier_id)
            from apps.models.supplier_db import Supplier
            from apps.extensions import db
            supplier_obj = db.session.get(Supplier, supplier_id)
            supplier_name = supplier_obj.trade_name if (supplier_obj and hasattr(supplier_obj, 'trade_name') and supplier_obj.trade_name) else (supplier_obj.name if supplier_obj else "مورد محدد")

        from apps.models.order_items_db import OrderItem
        from apps.extensions import db
        
        item = OrderItem.query.filter_by(id=item_id, order_id=order_id).first()
        if item:
            item.supplier_id = supplier_id
            db.session.commit()

        return jsonify({
            'success': True,
            'message': 'تم تعيين المورد بنجاح',
            'supplier_name': supplier_name
        })
        
    except Exception as e:
        from apps.extensions import db
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
