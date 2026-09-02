# -*- coding: utf-8 -*-
# 📂 apps/supplier_service/service.py
"""
خدمة بوابة الموردين - محجوب أونلاين
Supplier Portal Business Logic & Authentication Service
"""

import random
from datetime import datetime, timedelta
from apps.models.supplier_db import Supplier, db
from apps.models.otp_db import OTPModel  # استدعاء جدول الـ OTP الخاص بك
from apps.whatsapp_service.service import WhatsAppService

class SupplierService:
    def __init__(self):
        self.wa_service = WhatsAppService()

    def generate_and_send_otp(self, phone: str, purpose: str = "login") -> dict:
        """توليد رمز OTP وتخزينه في جدول الـ OTP وإرساله عبر الواتساب"""
        clean_phone = phone.replace("+", "").strip()
        supplier = Supplier.query.filter_by(phone=clean_phone).first()
        
        if not supplier:
            return {"success": False, "error": "رقم الهاتف غير مسجل كمورد في المنصة"}

        # توليد رمز من 6 أرقام وصلاحية لمدة 10 دقائق
        otp_code = str(random.randint(100000, 999900))
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        # حفظ الرمز في جدول الـ otp_db
        otp_record = OTPModel(
            phone=clean_phone,
            code=otp_code,
            purpose=purpose,
            expires_at=expires_at,
            is_used=False
        )
        db.session.add(otp_record)
        db.session.commit()

        # صياغة رسالة الواتساب وإرسالها
        text = (
            "🔐 *بوابة موردي محجوب أونلاين*\n\n"
            f"رمز التحقق الخاص بك هو: *{otp_code}*\n\n"
            "⏰ هذا الرمز صالح لمدة 10 دقائق فقط. لا تقم بمشاركته مع أحد."
        )
        wa_result = self.wa_service.send_message(clean_phone, text)

        return {
            "success": True,
            "message": "تم إرسال رمز التحقق إلى واتساب بنجاح",
            "whatsapp_status": wa_result.get("status")
        }

    def verify_otp_code(self, phone: str, otp_code: str, purpose: str = "login") -> dict:
        """التحقق من صحة رمز الـ OTP من جدول الـ OTP"""
        clean_phone = phone.replace("+", "").strip()
        
        # البحث عن أحدث رمز غير مستخدم وفعّال لنفس رقم الهاتف والغرض
        otp_record = OTPModel.query.filter_by(
            phone=clean_phone,
            code=otp_code,
            purpose=purpose,
            is_used=False
        ).order_by(OTPModel.id.desc()).first()

        if not otp_record:
            return {"success": False, "error": "رمز التحقق غير صحيح"}

        if otp_record.expires_at < datetime.utcnow():
            return {"success": False, "error": "انتهت صلاحية رمز التحقق"}

        # تعليم الرمز كَمُستخدَم لكي لا يُعاد استخدامه
        otp_record.is_used = True
        db.session.commit()

        # جلب بيانات المورد المرتبط بهذا الرقم
        supplier = Supplier.query.filter_by(phone=clean_phone).first()
        if not supplier:
            return {"success": False, "error": "المورد غير موجود"}

        return {"success": True, "supplier": supplier}
