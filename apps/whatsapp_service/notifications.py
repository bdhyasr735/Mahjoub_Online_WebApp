# coding: utf-8
# 📂 apps/whatsapp_service/notifications.py

"""
WhatsApp Notification Service for Mahgoob Online
Handles automated notifications for orders (ORD-#), status updates, and courier/supplier alerts.
"""

import logging
from .whatsapp_api import send_text_message

logger = logging.getLogger(__name__)

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
        if 200 <= status < 300:
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
        return (200 <= status < 300), response

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
        if 200 <= status < 300:
            logger.info(f"✅ [WhatsApp Courier Alert] Sent for ORD-{order_id} to courier {courier_phone}")
            return True, response
        else:
            logger.error(f"❌ [WhatsApp Courier Error] Failed for ORD-{order_id}: {response}")
            return False, response
