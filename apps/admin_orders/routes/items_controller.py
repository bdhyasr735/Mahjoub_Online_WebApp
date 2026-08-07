from flask import Blueprint, request, jsonify, render_template
# استيراد النماذج وقاعدة البيانات الخاصة بك (مثلاً SQLAlchemy)
# from .models import Order, OrderItem, Supplier, db

items_bp = Blueprint('items_bp', __name__)

# 1. مسار تحديث المورد (الذي يستقبل طلب الـ fetch)
@items_bp.route('/admin/orders/<int:order_id>/item/<int:item_id>/assign-supplier', methods=['POST'])
def assign_supplier(order_id, item_id):
    try:
        data = request.get_json()
        supplier_id = data.get('supplier_id')
        
        # تحويل القيمة الفارغة إلى None إذا اختار المستخدم "-- بدون مورد --"
        if supplier_id == "":
            supplier_id = None
        else:
            supplier_id = int(supplier_id) if supplier_id else None

        # جلب العنصر من قاعدة البيانات وتحديثه
        # item = OrderItem.query.filter_by(id=item_id, order_id=order_id).first_or_404()
        # item.supplier_id = supplier_id
        # db.session.commit()

        # جلب اسم المورد الجديد لإرساله للواجهة لتحديثه فوراً
        supplier_name = "-- بدون مورد --"
        if supplier_id:
            # supplier = Supplier.query.get(supplier_id)
            # supplier_name = supplier.trade_name or supplier.name
            pass

        return jsonify({
            'success': True,
            'message': 'تم تعيين المورد بنجاح',
            'supplier_name': supplier_name
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
