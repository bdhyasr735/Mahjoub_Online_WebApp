# coding: utf-8
# 📂 apps/suppliers_auth_portal/auth_service.py - خدمة إرسال التحقق للموردين عبر Twilio (الإصدار السيادي المستقر)

import os
import re
from twilio.rest import Client

class VendorAuthService:
    @staticmethod
    def initiate_login(phone, otp_code):
        """
        إرسال رمز التحقق الـ OTP الخاص بالموردين والمسوقين عبر خدمة Twilio الرسمية.
        """
        # 1. جلب بيانات التوثيق الصارمة من متغيرات بيئة ريندر (Render)
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        twilio_number = os.environ.get('TWILIO_NUMBER')

        # تحقق أمني استباقي من اكتمال تهيئة السيرفر للمتغيرات الثلاثة
        if not all([account_sid, auth_token, twilio_number]):
            print("🚨 [Twilio Config Error] بيانات التوثيق غير مكتملة في متغيرات البيئة بـ Render!")
            return False

        # 2. تنظيف الرقم وتجهيز الصياغة الدولية المعتمدة لـ Twilio
        clean_phone = re.sub(r'[^\d]', '', str(phone))
        
        # ضبط مدخلات الرقم اليمني المحلي تلقائياً ليطابق البنية الدولية
        if clean_phone.startswith('00967'):
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('7') and len(clean_phone) == 9:
            clean_phone = '967' + clean_phone
        elif clean_phone.startswith('07') and len(clean_phone) == 10:
            clean_phone = '967' + clean_phone[1:]
        
        # إضافة علامة الزائد (+) الإلزامية لبروتوكول Twilio
        destination_phone = f"+{clean_phone}"

        # 3. صياغة الرسالة الرسمية المعتمدة لهوية محجوب أونلاين
        message_body = (
            f"Mahjoub Online | الشركاء والموردين\n\n"
            f"رمز التحقق الأمني الخاص بك هو: {otp_code}\n\n"
            f"يرجى عدم مشاركة هذا الرمز مع أي شخص.\n"
            f"— محجوب أونلاين | سوقك الذكي"
        )

        try:
            # 4. بناء الجلسة البرمجية مع سيرفرات Twilio
            client = Client(account_sid, auth_token)

            # 5. التمييز الذكي لنوع قناة الإرسال (WhatsApp أو SMS عادية) بناءً على طبيعة رقم المرسل
            # إذا كان رقم المرسل في البيئة مسبوقاً بـ 'whatsapp:' أو تم تهيئته للواتساب، يتم ربطه كقناة واتساب تلقائياً
            if twilio_number.startswith('whatsapp:') or "whatsapp" in twilio_number.lower():
                from_number = twilio_number if twilio_number.startswith('whatsapp:') else f"whatsapp:{twilio_number}"
                to_number = f"whatsapp:{destination_phone}"
            else:
                from_number = twilio_number
                to_number = destination_phone

            # 6. إطلاق طلب الإرسال الفعلي
            message = client.messages.create(
                body=message_body,
                from_=from_number,
                to=to_number
            )

            print(f"✅ [Vendor OTP Sent via Twilio] تم الإرسال والمصادقة بنجاح! كود الرسالة المرجعي: {message.sid} للرقم: {to_number}")
            return True

        except Exception as e:
            print(f"🚨 CRITICAL [Vendor Twilio Error]: {str(e)}")
            return False
