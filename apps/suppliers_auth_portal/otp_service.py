# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/otp_service.py
"""
خدمة إدارة رموز التحقق (OTP) لبوابة الموردين - تعتمد على جدول otp_db.py
"""

import threading
import sys
import traceback
from flask import current_app
from apps.models.otp_db import OTP
from apps.whatsapp_service.service import WhatsAppService

class SupplierOTPService:
    @staticmethod
    def _format_phone_number(identifier: str) -> str:
        """توحيد تنسيق رقم الهاتف ليصبح بصيغة دولية صحيحة (967...)"""
        clean = identifier.replace("+", "").strip()
        
        # إذا كان رقماً محلياً يبدأ بـ 0 ويليها 7 (مثل 077xxxxxx)
        if clean.startswith("07") and len(clean) == 10:
            clean = f"967{clean[1:]}"
        # إذا كان رقماً محلياً يبدأ بـ 7 مباشرة ويتكون من 9 أرقام (مثل 77xxxxxx)
        elif clean.startswith("7") and len(clean) == 9:
            clean = f"967{clean}"
            
        return clean

    @staticmethod
    def _send_whatsapp_in_background(phone: str, text: str, app_obj=None):
        """دالة خاصة لإرسال الواتساب في الخلفية مع سياق التطبيق وطباعة الأخطاء بدقة"""
        def execute_send():
            try:
                whatsapp = WhatsAppService()
                result = whatsapp.send_message(recipient_phone=phone, text=text)
                print(f"📬 [OTP WhatsApp Result]: {result}", file=sys.stderr)
            except Exception as e:
                print(f"❌ [خطأ قاتل في إرسال OTP بالخلفية]: {str(e)}", file=sys.stderr)
                traceback.print_exc()

        if app_obj:
            with app_obj.app_context():
                execute_send()
        else:
            execute_send()

    @staticmethod
    def generate_and_send_otp(identifier: str, target_id: int, target_type: str = 'supplier', ip_address: str = None, user_agent: str = None) -> dict:
        """توليد رمز التحقق، تنسيق الرقم، وإرساله في الخلفية"""
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
            
            # 2. تجهيز النص (مع تحسين التنسيق)
            message_text = f"🔐 رمز التحقق الخاص بك في منصة محجوب أونلاين هو: *{otp_code}*\nصالح لمدة 5 دقائق فقط."
            
            # التقاط سياق التطبيق الحالي لضمان عمل الاتصال وقاعدة البيانات داخل الـ Thread
            app_obj = current_app._get_current_object() if current_app else None

            # 3. الإرسال في الخلفية لمنع الـ Timeout والخطأ 499
            thread = threading.Thread(
                target=SupplierOTPService._send_whatsapp_in_background,
                args=(recipient_phone, message_text, app_obj)
            )
            thread.daemon = True
            thread.start()
            
            return {"success": True, "message": "تم إنشاء وإرسال رمز التحقق بنجاح", "otp_code": otp_code}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def verify_otp(identifier: str, entered_otp: str) -> dict:
        """التحقق من صحة الرمز مع مطابقة آخر 9 أرقام لضمان المرونة"""
        formatted_identifier = SupplierOTPService._format_phone_number(identifier)
        clean_code = str(entered_otp).strip()
        
        # ملاحظة: إذا كان جدول OTP يدعم البحث جزئياً، يمكنك تمرير الصيغة المنسقة
        verification_result = OTP.verify_code_for_identifier(formatted_identifier, clean_code)
        return verification_result
