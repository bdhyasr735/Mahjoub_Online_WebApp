# coding: utf-8
# 📂 apps/admin_orders/routes/actions.py

from flask import Blueprint, request, jsonify
from flask_login import login_required
from apps.extensions import db
from apps.models.order_items_db import OrderItem

# هذا الملف مخصص فقط لعمليات تفاصيل الطلب (مثل تعديل بيانات العناصر، صور، إلخ)
actions_bp = Blueprint('actions_bp', __name__, url_prefix='/admin/orders/actions')

@actions_bp.route('/<string:item_id>/update-details', methods=['POST'])
@login_required
def update_item_details(item_id):
    """
    مسار مخصص لتحديث تفاصيل عنصر في الطلب 
    (مثل تحديث رابط صورة، ملاحظات المنتج، أو بيانات إضافية)
    """
    try:
        item = db.session.get(OrderItem, item_id)
        if not item:
            return jsonify({'success': False, 'message': 'العنصر غير موجود'}), 404
        
        data = request.get_json() or {}
        
        # ✅ تصحيح: تحديث حقل product_image بدلاً من image_url ليتطابق مع الموديل
        if 'image_url' in data:
            item.product_image = data['image_url']
            
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم تحديث تفاصيل المنتج بنجاح'})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@actions_bp.route('/<string:order_id>/refresh-items', methods=['POST'])
@login_required
def refresh_order_items_display(order_id):
    """
    مسار لجلب بيانات العناصر (صور/وصف) لغرض العرض فقط 
    بدون التأثير على حالة الطلب أو مزامنته مع السيرفر الرئيسي.
    """
    try:
        items = OrderItem.query.filter_by(order_id=order_id).all()
        # هنا يمكنك إضافة منطق لجلب صور المنتجات أو بيانات إضافية للعرض
        return jsonify({
            'success': True, 
            'items_count': len(items),
            'message': 'تم تحديث بيانات عرض العناصر'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
