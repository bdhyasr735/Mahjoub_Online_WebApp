# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/otp_service.py
"""
خدمة إدارة رموز التحقق (OTP) لبوابة الموردين - محجوب أونلاين
"""

import random
from datetime import datetime, timedelta
from apps.whatsapp_service.service import WhatsAppService
from apps.models.supplier_db import Supplier
from apps.extensions import db

class SupplierOTPService:
    @staticmethod
    def generate_and_send_otp(phone: str) -> dict:
        """توليد رمز تحقق عشوائي (6 أرقام)، حفظه، وإرساله عبر خدمة الواتساب"""
        clean_phone = phone.replace("+", "").strip()
        
        # 1. توليد رمز تحقق مكون من 6 أرقام
        otp_code = str(random.randint(100000, 999999))
        
        # 2. تحديد وقت انتهاء صلاحية الرمز (مثلاً خلال 5 دقائق)
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        try:
            # 3. البحث عن المورد لتحديث الرمز في سجله، أو التعامل مع رقم جديد
            supplier = Supplier.query.filter_by(phone=clean_phone).first()
            if supplier:
                supplier.otp_code = otp_code
                supplier.otp_expires_at = expires_at
                db.session.commit()
            
            # 4. تجهيز النص وإرساله عبر WhatsAppService
            whatsapp = WhatsAppService()
            message_text = f"🔐 رمز التحقق الخاص بك في منصة محجوب أونلاين هو: {otp_code}\nصالح لمدة 5 دقائق فقط."
            
            result = whatsapp.send_message(recipient_phone=clean_phone, text=message_text)
            
            if result.get("status") == "failed" or "error" in result:
                return {"success": False, "error": "فشل إرسال رسالة الواتساب عبر واجهة ميتا"}
                
            return {"success": True, "message": "تم إرسال رمز التحقق بنجاح", "otp_code": otp_code}
            
        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    def verify_otp(phone: str, entered_otp: str) -> bool:
        """التحقق من صحة رمز المدخل ومطابقته للوقت المسموح"""
        clean_phone = phone.replace("+", "").strip()
        supplier = Supplier.query.filter_by(phone=clean_phone).first()
        
        if not supplier or not supplier.otp_code or not supplier.otp_expires_at:
            return False
            
        # التحقق من انتهاء الصلاحية
        if datetime.utcnow() > supplier.otp_expires_at:
            return False
            
        # مطابقة الرمز
        if supplier.otp_code == entered_otp.strip():
            # مسح الرمز بعد نجاح التحقق لمرة واحدة
            supplier.otp_code = None
            supplier.otp_expires_at = None
            db.session.commit()
            return True
            
        return False
