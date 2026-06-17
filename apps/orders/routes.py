# 📂 apps/orders/routes.py
from flask import Blueprint, request, jsonify
from apps.extensions import db
from apps.models.orders_db import ProcessedOrder
import logging

# تعريف الـ Blueprint الخاص بالطلبات
orders_blueprint = Blueprint('orders', __name__)

# إعداد الـ Logger لمراقبة عمليات المزامنة
logger = logging.getLogger(__name__)

@orders_blueprint.route('/api/webhook/salla/orders', methods=['POST'])
def sync_order_webhook():
    """
    مسار استقبال الطلبات من سلة (Webhook).
    يستقبل البيانات، يستخرج المعرف والقيمة، ويقوم بحفظها مشفرة.
    """
    try:
        data = request.json
        if not data or 'data' not in data:
            return jsonify({"error": "Invalid payload"}), 400

        order_info = data['data']
        order_id = str(order_info.get('id'))
        total_price = order_info.get('total', {}).get('amount', 0.0)

        # التحقق إذا كان الطلب موجوداً مسبقاً لتجنب التكرار (Idempotency)
        existing_order = ProcessedOrder.query.filter_by(id=order_id).first()
        
        if existing_order:
            return jsonify({"message": "Order already exists"}), 200

        # إنشاء سجل جديد
        # التشفير يحدث تلقائياً بفضل الـ setter في المودل الذي أرفقته
        new_order = ProcessedOrder(
            id=order_id,
            status=order_info.get('status', 'paid')
        )
        new_order.total_price = total_price  # يتم تشفيره هنا تلقائياً

        db.session.add(new_order)
        db.session.commit()

        logger.info(f"✅ تم حفظ الطلب {order_id} بنجاح.")
        return jsonify({"message": "Order synced successfully"}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ أثناء مزامنة الطلب: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@orders_blueprint.route('/api/orders/sync-status', methods=['GET'])
def get_sync_status():
    """
    مسار اختياري للتأكد من عمل النظام والتحقق من عدد الطلبات المشفرة.
    """
    count = ProcessedOrder.query.count()
    return jsonify({"total_processed_orders": count, "status": "active"}), 200
