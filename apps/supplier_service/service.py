# -*- coding: utf-8 -*-
# 📂 apps/supplier_service/service.py
"""
خدمة بوابة الموردين - محجوب أونلاين
Supplier Portal Business Logic & Authentication Service
"""

from datetime import datetime
from apps.models.supplier_db import Supplier, db
from apps.models.otp_db import OTPModel
from apps.whatsapp_service.service import WhatsAppService

class SupplierService:
    def __init__(self):
        self.wa_service = WhatsAppService()

    def verify_otp_code(self, phone: str, otp_code: str, purpose: str = "login") -> dict:
        """التحقق من صحة رمز الـ OTP من جدول الـ OTP المستقل"""
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
        return Supplier.query.get(supplier_id)
