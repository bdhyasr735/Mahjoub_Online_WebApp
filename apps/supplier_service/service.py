# -*- coding: utf-8 -*-
# 📂 apps/supplier_service/service.py
"""
خدمة بوابة الموردين - محجوب أونلاين
Supplier Portal Business Logic & Authentication Service
"""

from datetime import datetime, timedelta
import random
from apps.whatsapp_service.service import WhatsAppService

class SupplierService:
    def __init__(self):
        self.wa_service = WhatsAppService()

    def verify_otp_code(self, phone: str, otp_code: str, purpose: str = "login") -> dict:
        """التحقق من صحة رمز الـ OTP من جدول الـ OTP المستقل"""
        # استيراد محلي لتفادي Circular Import
        from apps.models.supplier_db import Supplier, db
        from apps.models.otp_db import OTPModel

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

    def reset_supplier_password(self, phone: str, otp_code: str, new_password_hash: str) -> dict:
        """التحقق من كود الاستعادة وتحديث كلمة المرور للمورد"""
        from apps.models.supplier_db import db

        verification = self.verify_otp_code(phone, otp_code, purpose="password_reset")
        if not verification.get("success"):
            return verification

        supplier = verification.get("supplier")
        
        # تحديث كلمة المرور في نموذج المورد
        supplier.password = new_password_hash  # أو password_hash حسب عمود الجدول لديك
        db.session.commit()

        return {"success": True, "message": "تم تحديث كلمة المرور بنجاح"}

    def get_supplier_profile(self, supplier_id: int):
        """جلب بيانات الملف الشخصي للمورد"""
        from apps.models.supplier_db import Supplier
        return Supplier.query.get(supplier_id)

    def send_login_otp(self, phone: str) -> dict:
        """إرسال رمز تحقق OTP عبر واتساب لتسجيل الدخول"""
        from apps.models.supplier_db import Supplier, db
        from apps.models.otp_db import OTPModel

        clean_phone = phone.replace("+", "").strip()
        
        supplier = Supplier.query.filter_by(phone=clean_phone).first()
        if not supplier:
            return {"success": False, "error": "رقم الهاتف غير مسجل كـ مورد"}

        otp_code = str(random.randint(100000, 999999))
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        otp_record = OTPModel(
            phone=clean_phone,
            code=otp_code,
            purpose="login",
            expires_at=expires_at,
            is_used=False
        )
        db.session.add(otp_record)
        db.session.commit()

        message_body = f"رمز التحقق الخاص بك بوابـة الموردين في محجوب أونلاين هو: {otp_code}"
        wa_result = self.wa_service.send_message(phone=clean_phone, message=message_body)

        if not wa_result.get("success", True):
            return {"success": False, "error": "فشل إرسال رمز التحقق عبر واتساب"}

        return {"success": True, "message": "تم إرسال رمز التحقق بنجاح"}
