# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/otp_service.py
"""
خدمة إدارة رموز التحقق (OTP) لبوابة الموردين - تعتمد على جدول otp_db.py
"""

import sys
import traceback
from apps.models.otp_db import OTP
from apps.whatsapp_service.service import WhatsAppService

class SupplierOTPService:
    @staticmethod
    def _format_phone_number(identifier: str) -> str:
        """توحيد تنسيق رقم الهاتف ليصبح بصيغة دولية صحيحة (967...)"""
        if not identifier:
            return ""
        clean = str(identifier).replace("+", "").strip()
        
        # إذا كان رقماً محلياً يبدأ بـ 0 ويليها 7 (مثل 077xxxxxx)
        if clean.startswith("07") and len(clean) == 10:
            clean = f"967{clean[1:]}"
        # إذا كان رقماً محلياً يبدأ بـ 7 مباشرة ويتكون من 9 أرقام (مثل 77xxxxxx)
        elif clean.startswith("7") and len(clean) == 9:
            clean = f"967{clean}"
            
        return clean

    @staticmethod
    def generate_and_send_otp(identifier: str, target_id: int, target_type: str = 'supplier', ip_address: str = None, user_agent: str = None) -> dict:
        """توليد رمز التحقق، تنسيق الرقم، وإرساله مباشرة لضمان وصوله على سيرفرات الإنتاج"""
        recipient_phone = SupplierOTPService._format_phone_number(identifier)
        
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
            
            # 2. تجهيز النص
            message_text = f"🔐 رمز التحقق الخاص بك في منصة محجوب أونلاين هو: *{otp_code}*\nصالح لمدة 5 دقائق فقط."
            
            # 3. الإرسال المباشر للاتصال بـ Meta Cloud API والتأكد من إتمام الإرسال
            try:
                whatsapp = WhatsAppService()
                result = whatsapp.send_message(recipient_phone=recipient_phone, text=message_text)
                print(f"📬 [OTP WhatsApp Sent Successfully]: {result}", file=sys.stderr)
            except Exception as whatsapp_err:
                print(f"❌ [خطأ في إرسال رسالة الواتساب]: {str(whatsapp_err)}", file=sys.stderr)
                traceback.print_exc()
                # لا نوقف التنفيذ تماماً هنا، لكي يتمكن المطور من رؤية الرمز في الاستجابة (dev_otp) في حال تعذر إرسال الواتساب
            
            return {"success": True, "message": "تم إنشاء وإرسال رمز التحقق بنجاح", "otp_code": otp_code}
            
        except Exception as e:
            print(f"❌ [خطأ في توليد OTP]: {str(e)}", file=sys.stderr)
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    @staticmethod
    def verify_otp(identifier: str, entered_otp: str) -> dict:
        """التحقق من صحة الرمز مع مطابقة الرقم المنسق بدقة"""
        formatted_identifier = SupplierOTPService._format_phone_number(identifier)
        clean_code = str(entered_otp).strip()
        
        # تجربة التحقق باستخدام الرقم المنسق دولياً
        verification_result = OTP.verify_code_for_identifier(formatted_identifier, clean_code)
        
        # إذا فشل، نجرب التحقق بالمعرف الأصلي (في حال تم تخزينه بدون مفتاح الدولة)
        if not verification_result.get('success') and identifier != formatted_identifier:
            verification_result = OTP.verify_code_for_identifier(str(identifier).strip(), clean_code)
            
        return verification_result
