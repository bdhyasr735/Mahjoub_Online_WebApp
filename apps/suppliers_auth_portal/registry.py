# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/registry.py

import secrets
import string
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet, WalletTransaction, generate_unique_voucher_number
from apps.models.otp_db import OTP

class SupplierPortalRegistry:
    @staticmethod
    def register_new_supplier(data):
        """
        تسجيل مورد جديد بالكامل مع إنشاء محفظة مالية ورصيد افتتاحي وسندات خزينة.
        """
        try:
            username = data.get('username') or data.get('email').split('@')[0]
            email = data.get('email')
            phone = data.get('phone')
            password = data.get('password')
            company_name = data.get('company_name')
            owner_name = data.get('owner_name')
            full_address = data.get('full_address')

            # التحقق من عدم تكرار المورد
            existing = Supplier.query.filter(
                (Supplier.email == email) | (Supplier.phone == phone)
            ).first()
            
            if existing:
                return False, {"error": "البريد الإلكتروني أو رقم الهاتف مسجل مسبقاً."}

            # إنشاء المورد الجديد
            supplier = Supplier(
                username=username,
                email=email,
                phone=phone,
                trade_name=company_name,
                owner_name=owner_name,
                store_address=full_address,
                status='pending'  # بانتظار تفعيل الـ OTP
            )
            supplier.set_password(password)
            db.session.add(supplier)
            db.session.flush()

            # إنشاء محفظة مالية للمورد
            wallet = SupplierWallet(
                supplier_id=supplier.id,
                wallet_code=f"MAH-WEL963{supplier.id}",
                balance_sar=0.00,
                status='active'
            )
            db.session.add(wallet)
            db.session.commit()

            return True, {
                "supplier_id": supplier.id,
                "message": "تم إنشاء حساب المورد والمحفظة بنجاح."
            }
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def verify_supplier_otp(identifier, otp_code):
        """
        التحقق من رمز OTP الحقيقي عبر نموذج قاعدة البيانات OTP وتفعيل حساب المورد.
        """
        try:
            # التحقق باستخدام جدول قاعدة البيانات OTP الفعلي
            otp_obj = OTP.get_valid_otp(otp_code, identifier)
            if not otp_obj:
                otp_obj = OTP.get_valid_otp(otp_code)

            if not otp_obj:
                return False, "رمز التحقق غير صحيح أو انتهت صلاحيته."

            verification_result = otp_obj.verify(otp_code)
            if not verification_result.get("success"):
                return False, verification_result.get("message", "رمز التحقق غير صالح.")

            clean_phone = identifier[-9:] if identifier and identifier.isdigit() else identifier
            supplier = Supplier.query.filter(
                (Supplier.phone == identifier) | 
                (Supplier.search_phone == clean_phone) | 
                (Supplier.email == identifier) |
                (Supplier.username == identifier)
            ).first()

            if not supplier:
                return False, "لم يتم العثور على حساب مرتبط بهذه البيانات."

            supplier.status = 'active'
            db.session.commit()
            return True, "تم التحقق وتفعيل الحساب بنجاح."
        except Exception as e:
            db.session.rollback()
            return False, f"خطأ في قاعدة البيانات: {str(e)}"
