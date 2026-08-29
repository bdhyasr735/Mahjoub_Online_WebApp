# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/security.py
"""
بوابة دخول التجار - وحدة الأمان والتحقق والرسائل (واتساب + بريد إلكتروني بديل)
"""

import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask import session, request, flash, current_app

from apps.models.otp_db import OTP
from apps.whatsapp_service.service import WhatsAppService
from apps.models.supplier_db import Supplier

whatsapp_service = WhatsAppService()

# نظام الحماية وتتبع المحاولات الفاشلة (Rate Limiting)
FAILED_ATTEMPTS_STORE = {}

def validate_phone_number(phone):
    """التحقق من صحة تنسيق رقم الجوال اليمني أو الدولي"""
    if not phone:
        return False
    pattern = r'^(?:\+967|967)?(7[0137]\d{7}|0?[5]\d{8})$'
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    return bool(re.match(pattern, clean_phone))

def validate_email(email):
    """التحقق من صحة البريد الإلكتروني"""
    if not email:
        return False
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def check_rate_limit(ip_address, max_attempts=5, lockout_minutes=15):
    """حماية ضد هجمات القوة العمياء (Brute Force) وتجاوز المحاولات"""
    now = datetime.now()
    
    # تنظيف الذاكرة من المحاولات القديمة
    for key in list(FAILED_ATTEMPTS_STORE.keys()):
        attempts, lockout_until = FAILED_ATTEMPTS_STORE[key]
        if lockout_until and now > lockout_until:
            del FAILED_ATTEMPTS_STORE[key]
    
    if ip_address in FAILED_ATTEMPTS_STORE:
        attempts, lockout_until = FAILED_ATTEMPTS_STORE[ip_address]
        if lockout_until and now < lockout_until:
            remaining = int((lockout_until - now).total_seconds())
            return False, remaining
        elif lockout_until and now >= lockout_until:
            FAILED_ATTEMPTS_STORE[ip_address] = (0, None)
    
    return True, 0

def record_failed_attempt(ip_address, max_attempts=5, lockout_minutes=15):
    now = datetime.now()
    attempts, lockout_until = FAILED_ATTEMPTS_STORE.get(ip_address, (0, None))
    attempts += 1
    if attempts >= max_attempts:
        lockout_until = now + timedelta(minutes=lockout_minutes)
        FAILED_ATTEMPTS_STORE[ip_address] = (attempts, lockout_until)
        return lockout_minutes * 60
    else:
        FAILED_ATTEMPTS_STORE[ip_address] = (attempts, None)
        return 0

def clear_rate_limit(ip_address):
    if ip_address in FAILED_ATTEMPTS_STORE:
        del FAILED_ATTEMPTS_STORE[ip_address]


class SupplierAuthSecurity:
    
    @staticmethod
    def generate_and_send_otp(supplier: Supplier, channel: str = 'whatsapp') -> dict:
        """
        توليد رمز OTP وإرساله عبر الواتساب كخيار أساسي، وفي حال فشله أو طلبه يتم التبديل للإيميل كبديل.
        """
        try:
            # 1. تحديد المعرف الأساسي (رقم الجوال أو البريد)
            identifier = supplier.phone or supplier.email
            if not identifier:
                return {"success": False, "message": "لا يوجد رقم جوال أو بريد إلكتروني مسجل لهذا التاجر."}

            # 2. إنشاء رمز OTP جديد في قاعدة البيانات (صلاحية 5 دقائق = 300 ثانية)
            ip_addr = request.remote_addr if request else '127.0.0.1'
            ua_string = request.user_agent.string if request and request.user_agent else 'Web Portal'
            
            otp_record, otp_code = OTP.create_otp(
                identifier=identifier,
                target_id=supplier.id,
                target_type='supplier',
                ip_address=ip_addr,
                user_agent=ua_string,
                expiry_seconds=300
            )
            
            sent_successfully = False
            used_channel = channel

            # 3. محاولة الإرسال عبر الواتساب أولاً إذا طلب المستخدم وكان الجوال متاحاً
            if channel == 'whatsapp' and supplier.phone:
                welcome_name = supplier.store_name or supplier.owner_name or "عزيزنا التاجر"
                message_text = (
                    f"مرحباً بك {welcome_name} في سوق محجوب أونلاين 🛍️\n\n"
                    f"رمز التحقق الخاص بك لتسجيل الدخول هو: *{otp_code}*\n\n"
                    f"هذا الرمز صالح لمدة 5 دقائق. لا تشفه مع أحد."
                )
                
                wa_res = whatsapp_service.send_message(supplier.phone, message_text)
                if wa_res and wa_res.get('status') != 'failed' and 'error' not in wa_res:
                    sent_successfully = True
                else:
                    # فشل الواتساب، نتحول تلقائياً للبريد الإلكتروني كبديل آمن
                    used_channel = 'email'

            # 4. الإرسال عبر البريد الإلكتروني (إذا تم طلبه صراحة، أو كبديل تلقائي عند تعطل الواتساب)
            if (used_channel == 'email' or not sent_successfully) and supplier.email:
                email_sent = SupplierAuthSecurity._send_otp_email(supplier.email, otp_code, supplier.store_name or "التجار")
                if email_sent:
                    sent_successfully = True
                    used_channel = 'email'

            if sent_successfully:
                channel_name_ar = 'الواتساب' if used_channel == 'whatsapp' else 'البريد الإلكتروني'
                return {
                    "success": True, 
                    "channel": used_channel, 
                    "message": f"تم إرسال رمز التحقق بنجاح عبر {channel_name_ar}"
                }
            else:
                return {
                    "success": False, 
                    "message": "فشل إرسال رمز التحقق عبر القنوات المتاحة. تأكد من صحة رقم الجوال أو البريد."
                }

        except Exception as e:
            return {"success": False, "message": f"حدث خطأ أثناء توليد الرمز: {str(e)}"}

    @staticmethod
    def _send_otp_email(to_email: str, otp_code: str, store_name: str) -> bool:
        """إرسال رمز التحقق عبر SMTP البريد الإلكتروني كبديل للطوارئ"""
        try:
            smtp_server = os.getenv("MAIL_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("MAIL_PORT", 587))
            smtp_user = os.getenv("MAIL_USERNAME", "")
            smtp_password = os.getenv("MAIL_PASSWORD", "")
            sender_email = os.getenv("MAIL_DEFAULT_SENDER", smtp_user)

            if not smtp_user or not smtp_password:
                print("⚠️ [تحذير البريد]: إعدادات SMTP غير متوفرة في متغيرات البيئة.")
                return False

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Subject'] = 'رمز التحقق لتسجيل الدخول - سوق محجوب أونلاين'

            html_content = f"""
            <div dir="rtl" style="font-family: Arial, sans-serif; padding: 25px; background-color: #1a0b2e; color: #ffffff; border-radius: 12px; border: 1px solid #D4AF37;">
                <h2 style="color: #D4AF37; text-align: center;">سوق محجوب أونلاين 🛍️</h2>
                <p>مرحباً <b>{store_name}</b>،</p>
                <p>تلقينا طلباً لتسجيل الدخول إلى لوحة تحكم التجار الخاصة بك. إليك رمز التحقق:</p>
                <div style="background: #2b134d; color: #D4AF37; font-size: 28px; font-weight: bold; padding: 15px; text-align: center; border-radius: 8px; letter-spacing: 6px; margin: 25px 0; border: 1px dashed #D4AF37;">
                    {otp_code}
                </div>
                <p style="color: #cccccc; font-size: 14px;">هذا الرمز صالح لمدة 5 دقائق فقط. إذا لم تقم بطلب هذا الرمز، يرجى تجاهل هذه الرسالة بأمان.</p>
                <hr style="border: none; border-top: 1px solid #4a287a; margin: 20px 0;">
                <p style="font-size: 12px; color: #999999; text-align: center;">جميع الحقوق محفوظة © سوق محجوب أونلاين 2026</p>
            </div>
            """
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(sender_email, to_email, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"⚠️ [خطأ إرسال الإيميل البديل]: {e}")
            return False

    @staticmethod
    def verify_supplier_otp(identifier: str, otp_code: str) -> dict:
        """التحقق من صحة الرمز المدخل عبر نموذج OTP"""
        otp_obj = OTP.get_valid_otp(otp_code, identifier)
        if not otp_obj:
            # محاولة بحث عامة إذا لم يُطابق المعرف تماماً
            otp_obj = OTP.get_valid_otp(otp_code)
            
        if not otp_obj:
            return {"success": False, "message": "رمز التحقق غير صحيح أو انتهت صلاحيته."}
        
        # استدعاء دالة التحقق من الموديل
        result = otp_obj.verify(otp_code)
        return result
