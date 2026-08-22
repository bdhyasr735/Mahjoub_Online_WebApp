# coding: utf-8
# 📂 apps/whatsapp_service/notifications.py

"""
WhatsApp Notification Service for Mahgoob Online
Handles automated notifications for orders (ORD-#), status updates, and courier/supplier alerts.
"""

import os
import logging
from datetime import datetime
from flask import current_app

try:
    from .whatsapp_api import send_text_message
except ImportError:
    from apps.whatsapp_service.whatsapp_api import send_text_message

try:
    from apps.models.whatsapp_models import WhatsAppMessageLog, WhatsAppCustomerContact
except ImportError:
    from .models.whatsapp_models import WhatsAppMessageLog, WhatsAppCustomerContact

logger = logging.getLogger(__name__)


def get_db():
    """Helper to get db instance safely from main app"""
    try:
        from apps.extensions import db
        return db
    except ImportError:
        try:
            from app import db
            return db
        except ImportError:
            return None


def _log_outbound_notification(recipient_phone, message, order_id=None, success=False, response_data=None):
    """دالة مساعدة لتسجيل الرسائل التلقائية في قاعدة البيانات لضمان ظهورها بلوحة التحكم"""
    db = get_db()
    if not db:
        return

    try:
        phone_id = 'system'
        if current_app:
            phone_id = current_app.config.get('WHATSAPP_PHONE_NUMBER_ID') or os.environ.get('WHATSAPP_PHONE_NUMBER_ID', 'system')
        else:
            phone_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', 'system')
        
        wamid = None
        if success and isinstance(response_data, dict):
            messages = response_data.get('messages', [])
            if messages:
                wamid = messages[0].get('id')

        outbound_log = WhatsAppMessageLog(
            wamid=wamid,
            direction='outbound',
            sender_number=phone_id,
            recipient_number=recipient_phone,
            message_type='text',
            content=message,
            status='sent' if success else 'failed'
        )
        db.session.add(outbound_log)
        
        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=recipient_phone).first()
        if contact:
            contact.last_message = f"إلى: {message[:50]}..."
            contact.last_timestamp = datetime.utcnow()
        else:
            new_contact = WhatsAppCustomerContact(
                phone=recipient_phone,
                name=f"عميل ({recipient_phone})",
                last_message=f"إلى: {message[:50]}...",
                last_timestamp=datetime.utcnow(),
                unread_count=0
            )
            db.session.add(new_contact)

        db.session.commit()
    except Exception as e:
        logger.error(f"❌ [DB Notification Log Error]: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass


class WhatsAppNotifier:
    
    @staticmethod
    def send_order_confirmation(customer_phone, order_id, total_price, customer_name="عميلنا العزيز"):
        """
        إرسال إشعار تأكيد الطلب للعميل فور إتمام عملية الشراء.
        """
        message = (
            f"مرحباً بـ {customer_name}! 👋\n\n"
            f"شكراً لتسوقك في *محجوب أونلاين*. لقد تم استلام طلبك بنجاح وجاري تجهيزه.\n\n"
            f"📦 *رقم الطلب:* ORD-{order_id}\n"
            f"💰 *إجمالي المبلغ:* {total_price}\n\n"
            f"سنقوم بإشعارك بكل مستجدات الشحن والتوصيل. شكراً لثقتك بنا! 🚀"
        )
        
        status, response = send_text_message(customer_phone, message)
        success = (200 <= status < 300)
        
        # حفظ الرسالة في السجلات وقاعدة البيانات تلقائياً
        _log_outbound_notification(customer_phone, message, order_id=order_id, success=success, response_data=response)

        if success:
            logger.info(f"✅ [WhatsApp Notification] Order confirmation sent for ORD-{order_id} to {customer_phone}")
            return True, response
        else:
            logger.error(f"❌ [WhatsApp Notification Error] Failed to send order confirmation for ORD-{order_id}: {response}")
            return False, response

    @staticmethod
    def send_order_status_update(customer_phone, order_id, new_status, customer_name="عميلنا العزيز"):
        """
        إرسال إشعار بتحديث حالة الطلب (قيد التجهيز، خرج للوصول، تم التسليم).
        """
        status_messages = {
            "processing": "جاري تجهيز طلبك وتغليفه بعناية.",
            "out_for_delivery": "مندوب التوصيل في طريقه إليك الآن! 🚗",
            "delivered": "تم تسليم الطلب بنجاح. نتمنى أن نكون عند حسن ظنك! ⭐",
            "cancelled": "نأسف لإبلاغك بأنه تم إلغاء الطلب."
        }
        
        status_text = status_messages.get(new_status, f"تم تحديث حالة طلبك إلى: {new_status}")
        
        message = (
            f"عزيزي {customer_name},\n"
            f"تحديث بخصوص طلبك *ORD-{order_id}*:\n\n"
            f"📌 *الحالة:* {status_text}\n\n"
            f"مع تحيات إدارة *محجوب أونلاين*."
        )
        
        status, response = send_text_message(customer_phone, message)
        success = (200 <= status < 300)
        
        _log_outbound_notification(customer_phone, message, order_id=order_id, success=success, response_data=response)
        return success, response

    @staticmethod
    def send_courier_alert(courier_phone, order_id, delivery_address, customer_phone):
        """
        إرسال إشعار تنبيه للساعي/المندوب بتفاصيل الطلب الجديد الموجه إليه.
        """
        message = (
            f"🚨 *تنبيه مهمة توصيل جديدة*\n\n"
            f"تم تكليفك بتوصيل الطلب:\n"
            f"📦 *رقم الطلب:* ORD-{order_id}\n"
            f"📍 *عنوان التوصيل:* {delivery_address}\n"
            f"📞 *هاتف العميل:* {customer_phone}\n\n"
            f"يرجى التأكيد والتحرك في أسرع وقت. بالتوفيق!"
        )
        
        status, response = send_text_message(courier_phone, message)
        success = (200 <= status < 300)
        
        _log_outbound_notification(courier_phone, message, order_id=order_id, success=success, response_data=response)

        if success:
            logger.info(f"✅ [WhatsApp Courier Alert] Sent for ORD-{order_id} to courier {courier_phone}")
            return True, response
        else:
            logger.error(f"❌ [WhatsApp Courier Error] Failed for ORD-{order_id}: {response}")
            return False, response
