# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/otp_service.py
"""
خدمة إدارة رموز التحقق (OTP) لبوابة الموردين - تعتمد على جدول otp_db.py
"""

from apps.models.otp_db import OTP
from apps.whatsapp_service.service import WhatsAppService

class SupplierOTPService:
    @staticmethod
    def generate_and_send_otp(identifier: str, target_id: int, target_type: str = 'supplier', ip_address: str = None, user_agent: str = None) -> dict:
        """توليد رمز تحقق آمن عبر جدول OTP، حفظه، وإرساله عبر خدمة الواتساب"""
        clean_identifier = identifier.replace("+", "").strip()
        
        try:
            # 1. استدعاء دالة الإنشاء الآمنة من نموذج OTP (تنشئ الرمز المشفر وتُبطِل أي رموز سابقة)
            otp_record, otp_code = OTP.create_otp(
                identifier=clean_identifier,
                target_id=target_id,
                target_type=target_type,
                ip_address=ip_address,
                user_agent=user_agent,
                expiry_seconds=300 # صالح لمدة 5 دقائق
            )
            
            # 2. تجهيز النص وإرساله عبر WhatsAppService
            whatsapp = WhatsAppService()
            message_text = f"🔐 رمز التحقق الخاص بك في منصة محجوب أونلاين هو: *{otp_code}*\nصالح لمدة 5 دقائق فقط."
            
            result = whatsapp.send_message(recipient_phone=clean_identifier, text=message_text)
            
            if result.get("status") == "failed" or "error" in result:
                return {"success": False, "error": "فشل إرسال رسالة الواتساب عبر واجهة ميتا"}
                
            return {"success": True, "message": "تم إرسال رمز التحقق بنجاح", "otp_code": otp_code}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def verify_otp(identifier: str, entered_otp: str) -> dict:
        """التحقق من صحة الرمز المدخل عبر دوال الأمان في نموذج OTP"""
        clean_identifier = identifier.replace("+", "").strip()
        clean_code = str(entered_otp).strip()
        
        # استخدام دالة التحقق المضمنة في نموذج OTP والتي تدير المحاولات والحظر تلقائياً
        verification_result = OTP.verify_code_for_identifier(clean_identifier, clean_code)
        return verification_result
