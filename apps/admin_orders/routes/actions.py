# coding: utf-8
# 📂 apps/admin_orders/routes/actions.py

from flask import Blueprint, request, jsonify
from apps.services.graphql_client import GraphQLClient
from apps.services.order_service import OrderService

actions_bp = Blueprint('actions_bp', __name__)

@actions_bp.route('/admin/orders/<string:order_id>/sync', methods=['POST'])
def sync_order_action(order_id):
    """مسار خاص لإعادة مزامنة طلب معين من سيرفر Qumra"""
    try:
        # إنشاء العميل والخدمة
        client = GraphQLClient()
        service = OrderService(client)
        
        # تنفيذ المزامنة
        synced_order = service.sync_single_order(order_id)
        
        if synced_order:
            return jsonify({
                'success': True, 
                'message': 'تم تحديث الطلب بنجاح من الخادم', 
                'order_id': order_id
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'فشل جلب الطلب من الخادم، تأكد من معرف الطلب'
            }), 404
            
    except Exception as e:
        print(f"❌ [Actions] خطأ أثناء المزامنة: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
