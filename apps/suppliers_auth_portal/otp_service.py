# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/otp_service.py
"""
خدمة إدارة رموز التحقق (OTP) لبوابة الموردين - تعتمد على جدول otp_db.py
"""

import threading
from apps.models.otp_db import OTP
from apps.whatsapp_service.service import WhatsAppService

class SupplierOTPService:
    @staticmethod
    def _send_whatsapp_in_background(phone: str, text: str):
        """دالة خاصة لإرسال الواتساب في الخلفية لعدم تجميد السيرفر"""
        try:
            whatsapp = WhatsAppService()
            whatsapp.send_message(recipient_phone=phone, text=text)
        except Exception as e:
            print(f"⚠️ [خطأ إرسال الواتساب بالخلفية]: {e}")

    @staticmethod
    def generate_and_send_otp(identifier: str, target_id: int, target_type: str = 'supplier', ip_address: str = None, user_agent: str = None) -> dict:
        """توليد رمز التحقق آمن، معالجة الرقم، وإرساله عبر خيط خلفي لمنع الـ Timeout"""
        raw_identifier = identifier.replace("+", "").strip()
        
        # معالجة تنسيق رقم الهاتف ليصبح دولياً بشكل تلقائي (خاص باليمن 967)
        if raw_identifier.startswith("7") and len(raw_identifier) == 9:
            recipient_phone = f"967{raw_identifier}"
        else:
            recipient_phone = raw_identifier  # إذا كان رقماً كاملاً مسبقاً أو بريداً إلكترونياً
        
        try:
            # 1. توليد الرمز وحفظه في قاعدة البيانات بالرقم المُنسق
            otp_record, otp_code = OTP.create_otp(
                identifier=recipient_phone,
                target_id=target_id,
                target_type=target_type,
                ip_address=ip_address,
                user_agent=user_agent,
                expiry_seconds=300  # صالح لمدة 5 دقائق
            )
            
            # 2. تجهيز النص متضمناً الرمز المُولّد
            message_text = f"🔐 رمز التحقق الخاص بك في منصة محجوب أونلاين هو: *{otp_code}*\nصالح لمدة 5 دقائق فقط."
            
            # 3. إرسال الواتساب في الخلفية (Thread) بالرقم الصحيح
            thread = threading.Thread(
                target=SupplierOTPService._send_whatsapp_in_background,
                args=(recipient_phone, message_text)
            )
            thread.daemon = True
            thread.start()
            
            return {"success": True, "message": "تم إنشاء وإرسال رمز التحقق بنجاح", "otp_code": otp_code}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def verify_otp(identifier: str, entered_otp: str) -> dict:
        """التحقق من صحة الرمز المدخل مع مراعاة توحيد الصيغة"""
        raw_identifier = identifier.replace("+", "").strip()
        if raw_identifier.startswith("7") and len(raw_identifier) == 9:
            clean_identifier = f"967{raw_identifier}"
        else:
            clean_identifier = raw_identifier
            
        clean_code = str(entered_otp).strip()
        
        verification_result = OTP.verify_code_for_identifier(clean_identifier, clean_code)
        return verification_result
