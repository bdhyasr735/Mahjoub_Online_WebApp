# coding: utf-8
# 📂 apps/api/webhooks.py - معالج الويب هوك السيادي (النسخة النهائية)

from flask import Blueprint, request, jsonify
import hmac
import hashlib
import logging
from apps.config import Config
from apps.extensions import db
from apps.models.orders_db import ProcessedOrder

# إعداد المسار
webhooks_bp = Blueprint('webhooks', __name__)
logger = logging.getLogger(__name__)

@webhooks_bp.route('/webhooks', methods=['POST'])
def handle_qumra_webhook():
    # 1. التحقق من التوقيع الأمني (Signature Verification)
    # نستخدم hmac للمطابقة مع المفتاح السري المسجل في الـ Config
    signature = request.headers.get('X-WebHook-Signature')
    if not signature:
        logger.warning("⚠️ محاولة وصول بدون توقيع!")
        return jsonify({"error": "Missing signature"}), 401

    secret = Config.WEBHOOK_SECRET.encode()
    payload = request.data
    expected_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        logger.error("🚫 محاولة وصول بتوقيع غير صالح!")
        return jsonify({"error": "Invalid signature"}), 403

    # 2. استخراج بيانات الويب هوك
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400
        
    event = data.get('event')
    order_data = data.get('data', {})

    logger.info(f"✅ تم استلام ويب هوك نوع: {event}")

    # 3. معالجة وحفظ الطلب
    # نتأكد من نوع الحدث ونقوم بعملية الحفظ/التحديث
    if event in ['order/created', 'order/updated']:
        order_id = str(order_data.get('id', ''))
        
        if order_id:
            # البحث عن الطلب الحالي أو إنشاء واحد جديد
            order = ProcessedOrder.query.get(order_id)
            if not order:
                order = ProcessedOrder(id=order_id)
            
            # تحديث الحالة
            order.status = order_data.get('status', 'pending')
            
            # تحديث القيمة المالية المشفرة
            # ملاحظة: الموديل سيقوم بتشفير القيمة تلقائياً عبر @total_price.setter
            total_amount = order_data.get('total', {}).get('amount', 0.0)
            order.total_price = float(total_amount)
            
            try:
                db.session.add(order)
                db.session.commit()
                logger.info(f"💾 تم حفظ/تحديث الطلب {order_id} بنجاح.")
            except Exception as e:
                db.session.rollback()
                logger.error(f"❌ خطأ أثناء حفظ الطلب {order_id}: {e}")
                return jsonify({"error": "Database error"}), 500

    return jsonify({"status": "success"}), 200
