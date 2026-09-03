# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/otp_service.py

import threading
from apps.models.otp_db import OTP
from apps.whatsapp_service.service import WhatsAppService

class SupplierOTPService:
    @staticmethod
    def _format_phone_number(identifier: str) -> str:
        """توحيد تنسيق رقم الهاتف ليصبح بصيغة دولية صحيحة (967...)"""
        clean = identifier.replace("+", "").strip()
        if clean.startswith("07") and len(clean) == 10:
            clean = f"967{clean[1:]}"
        elif clean.startswith("7") and len(clean) == 9:
            clean = f"967{clean}"
        return clean

    @staticmethod
    def _send_whatsapp_in_background(phone: str, text: str):
        """إرسال رسالة الواتساب عبر خيط خلفي لمنع تجميد السيرفر والـ Timeout"""
        try:
            whatsapp = WhatsAppService()
            whatsapp.send_message(recipient_phone=phone, text=text)
        except Exception as e:
            print(f"⚠️ [خطأ إرسال الواتساب بالخلفية]: {e}")

    @staticmethod
    def generate_and_send_otp(identifier: str, target_id: int, target_type: str = 'supplier', ip_address: str = None, user_agent: str = None) -> dict:
        recipient_phone = SupplierOTPService._format_phone_number(identifier)
        
        try:
            # 1. إنشاء وحفظ الرمز في قاعدة البيانات بالرقم المُنسق
            otp_record, otp_code = OTP.create_otp(
                identifier=recipient_phone,
                target_id=target_id,
                target_type=target_type,
                ip_address=ip_address,
                user_agent=user_agent,
                expiry_seconds=300
            )
            
            # 2. نص الرسالة
            message_text = f"🔐 رمز التحقق الخاص بك في منصة محجوب أونلاين هو: *{otp_code}*\nصالح لمدة 5 دقائق فقط."
            
            # 3. التشغيل في الخلفية لضمان سرعة الاستجابة ومنع خطأ 499
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
        formatted_identifier = SupplierOTPService._format_phone_number(identifier)
        clean_code = str(entered_otp).strip()
        return OTP.verify_code_for_identifier(formatted_identifier, clean_code)
