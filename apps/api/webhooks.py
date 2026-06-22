# coding: utf-8
# 📂 apps/api/webhooks.py - معالج الويب هوك السيادي (النسخة النهائية والمحكمة)

import hmac
import hashlib
import logging
from flask import Blueprint, request, jsonify
from config import Config 
from apps.extensions import db
# تم تحديث الاستيراد ليطابق الموديل الجديد Order
from apps.models.orders_db import Order

# إعداد السجلات
logger = logging.getLogger(__name__)
webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route('/webhooks', methods=['POST'])
def handle_qumra_webhook():
    """
    معالج الويب هوك: التحقق من التوقيع ثم معالجة بيانات الطلب.
    """
    
    # 1. التحقق من التوقيع (الأمن أولاً)
    signature = request.headers.get('X-WebHook-Signature') or request.headers.get('X-Signature')
    if not signature:
        logger.warning("⚠️ محاولة اتصال بدون توقيع")
        return jsonify({"error": "Missing signature"}), 401

    secret = Config.WEBHOOK_SECRET.strip().encode('utf-8')
    payload = request.get_data()
    expected_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        logger.error(f"🚫 توقيع غير صالح. متوقع: {expected_signature}, مستلم: {signature}")
        return jsonify({"error": "Invalid signature"}), 403

    # 2. استخراج البيانات
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    event = data.get('event')
    order_data = data.get('data', {})
    logger.info(f"✅ استلام حدث: {event} | البيانات: {order_data.get('id')}")

    # 3. معالجة وحفظ الطلب باستخدام الموديل Order المحدث
    if event in ['order/created', 'order/updated', 'cart/created']:
        order_id = str(order_data.get('id') or order_data.get('_id', ''))
        
        if order_id:
            try:
                # البحث عن الطلب الموجود أو إنشاء جديد
                order = Order.query.get(order_id) or Order(id=order_id)
                
                # تحديث المعلومات الأساسية
                order.status = order_data.get('status', 'pending')
                
                # استخراج السعر بأمان
                total_data = order_data.get('total')
                if isinstance(total_data, dict):
                    order.total_price = float(total_data.get('amount', 0.0))
                else:
                    order.total_price = float(order_data.get('total', 0.0))

                db.session.add(order)
                db.session.commit()
                logger.info(f"💾 تم حفظ الطلب {order_id} في قاعدة البيانات بنجاح.")
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"❌ فشل حفظ الطلب {order_id}: {str(e)}")
                return jsonify({"error": "Database error"}), 500

    return jsonify({"status": "success"}), 200
