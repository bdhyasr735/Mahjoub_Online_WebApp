# -*- coding: utf-8 -*-
# apps/suppliers_auth_portal/registry.py

from datetime import datetime, timedelta
import secrets
import string
import os
from cryptography.fernet import Fernet
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet, WalletTransaction, generate_unique_voucher_number
from apps.models.treasury_db import TreasuryEntry
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.otp_db import OTP


class SupplierPortalRegistry:
    """سجل الموردين - إدارة تسجيل الموردين وإنشاء المحافظ المالية والتحقق"""

    @staticmethod
    def _get_fernet():
        key = os.environ.get('ENCRYPTION_KEY', 'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8V=')
        try:
            return Fernet(key.encode('utf-8'))
        except Exception:
            import base64
            b64_key = base64.urlsafe_b64encode(key.encode('utf-8')[:32].ljust(32, b'0'))
            return Fernet(b64_key)

    @staticmethod
    def register_new_supplier(data):
        """
        تسجيل مورد جديد مع إنشاء محفظة مالية تلقائياً.
        
        Args:
            data (dict): بيانات التسجيل
                - company_name: اسم المنشأة
                - full_address: العنوان الكامل
                - owner_name: اسم المالك
                - email: البريد الإلكتروني
                - phone: رقم الهاتف
                - password: كلمة المرور
                - employees: قائمة الموظفين (اختياري)
        
        Returns:
            tuple: (success, result)
                - success: bool
                - result: dict (بيانات المورد أو رسالة خطأ)
        """
        try:
            # التحقق من وجود المستخدم مسبقاً
            existing_email = Supplier.query.filter_by(email=data.get('email')).first()
            if existing_email:
                return False, {"error": "البريد الإلكتروني مسجل مسبقاً"}

            existing_phone = Supplier.query.filter_by(search_phone=str(data.get('phone'))[-9:]).first()
            if existing_phone:
                return False, {"error": "رقم الهاتف مسجل مسبقاً"}

            # إنشاء اسم مستخدم فريد
            base_username = data.get('company_name', 'supplier').replace(' ', '_').lower()[:30]
            username = base_username
            counter = 1
            while Supplier.query.filter_by(username=username).first():
                username = f"{base_username}_{counter}"
                counter += 1

            # إنشاء المورد
            supplier = Supplier(
                username=username,
                email=data.get('email'),
                owner_name=data.get('owner_name'),
                trade_name=data.get('company_name'),
                store_name=data.get('company_name'),
                status='active',
                rank='bronze'
            )

            # تعيين رقم الهاتف (سيتم تشفيره تلقائياً)
            supplier.phone = data.get('phone')

            # تعيين كلمة المرور
            supplier.set_password(data.get('password'))

            db.session.add(supplier)
            db.session.flush()

            # إنشاء المحفظة المالية تلقائياً
            wallet = SupplierWallet(
                supplier_id=supplier.id,
                wallet_code=f"WEL-963{supplier.id}",
                status='active',
                balance_sar=0.00
            )
            db.session.add(wallet)
            db.session.flush()

            # إنشاء معاملة افتتاحية للمحفظة
            voucher_number = generate_unique_voucher_number(db.session.connection(), length=6, prefix="VCH-")
            reference_number = f"TRX-OPEN-{supplier.id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

            initial_transaction = WalletTransaction(
                wallet_id=wallet.id,
                trans_type='deposit',
                status='completed',
                amount=0.00,
                currency='SAR',
                balance_before=0.00,
                balance_after=0.00,
                reference_number=reference_number,
                voucher_number=voucher_number,
                description="رصيد افتتاحي للمحفظة عند التسجيل"
            )
            db.session.add(initial_transaction)
            db.session.flush()

            # إنشاء سند خزينة
            treasury_entry = TreasuryEntry(
                reference_number=reference_number,
                voucher_number=voucher_number,
                entry_type='deposit',
                amount=0.00,
                currency='SAR',
                owner_type='supplier',
                owner_id=supplier.id,
                description="سند افتتاح محفظة مورد جديد"
            )
            db.session.add(treasury_entry)

            # إضافة الموظفين إذا وجدوا
            employees = data.get('employees', [])
            for emp_data in employees:
                if emp_data.get('full_name') and emp_data.get('email'):
                    staff = SupplierStaff(
                        supplier_id=supplier.id,
                        username=emp_data.get('email').split('@')[0],
                        role=emp_data.get('role', 'staff'),
                        status='active'
                    )
                    staff.full_name = emp_data.get('full_name')
                    staff.email = emp_data.get('email')
                    staff.phone = emp_data.get('phone', '')
                    staff.set_password(secrets.token_urlsafe(8))  # كلمة مرور مؤقتة
                    db.session.add(staff)

            db.session.commit()

            return True, {
                "supplier": supplier.to_dict(),
                "wallet": wallet.to_dict(),
                "username": username
            }

        except Exception as e:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False, {"error": f"خطأ في تسجيل المورد: {str(e)}"}

    @staticmethod
    def verify_supplier_otp(identifier, otp_code):
        """
        التحقق من رمز OTP للمورد.
        
        Args:
            identifier: رقم الهاتف أو البريد الإلكتروني أو اسم المستخدم
            otp_code: رمز التحقق
        
        Returns:
            tuple: (success, message)
        """
        try:
            if not identifier or not otp_code:
                return False, "يرجى إدخال رمز التحقق"

            # البحث عن المورد
            clean_phone_suffix = str(identifier)[-9:] if str(identifier).isdigit() else identifier
            supplier = Supplier.query.filter(
                (Supplier.username == identifier) |
                (Supplier.email == identifier) |
                (Supplier.search_phone == clean_phone_suffix)
            ).first()

            if not supplier:
                return False, "المورد غير موجود"

            # التحقق من رمز OTP من قاعدة البيانات
            otp_record = OTP.query.filter(
                OTP.target_id == supplier.id,
                OTP.target_type == 'supplier',
                OTP.is_used == False,
                OTP.expiry > datetime.utcnow()
            ).first()

            if otp_record:
                # التحقق من الرمز
                verification_result = otp_record.verify(otp_code)
                if verification_result.get('success'):
                    supplier.status = 'active'
                    db.session.commit()
                    return True, "تم التحقق بنجاح وتفعيل الحساب"
                else:
                    return False, verification_result.get('message', 'رمز التحقق غير صحيح')

            # إذا لم يوجد OTP في قاعدة البيانات، نستخدم الرمز التجريبي
            if otp_code == "123456":
                supplier.status = 'active'
                db.session.commit()
                return True, "تم التحقق بنجاح (وضع التطوير)"

            return False, "رمز التحقق غير صحيح أو منتهي الصلاحية"

        except Exception as e:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False, f"خطأ في التحقق: {str(e)}"

    @staticmethod
    def resend_otp(identifier):
        """
        إعادة إرسال رمز التحقق.
        
        Args:
            identifier: رقم الهاتف أو البريد الإلكتروني
        
        Returns:
            tuple: (success, message)
        """
        try:
            # البحث عن المورد
            clean_phone_suffix = str(identifier)[-9:] if str(identifier).isdigit() else identifier
            supplier = Supplier.query.filter(
                (Supplier.username == identifier) |
                (Supplier.email == identifier) |
                (Supplier.search_phone == clean_phone_suffix)
            ).first()

            if not supplier:
                return False, "المورد غير موجود"

            # إنشاء رمز OTP جديد
            otp_record, otp_code = OTP.create_otp(
                identifier=supplier.phone or supplier.email,
                target_id=supplier.id,
                target_type='supplier',
                expiry_seconds=300
            )

            # في الإنتاج: أرسل الرمز عبر SMS أو Email
            # هنا نعيد الرمز للتطوير فقط
            return True, {
                "message": "تم إرسال رمز تحقق جديد",
                "otp_code": otp_code  # للتطوير فقط - احذفه في الإنتاج
            }

        except Exception as e:
            db.session.rollback()
            return False, f"خطأ في إعادة الإرسال: {str(e)}"

    @staticmethod
    def request_password_reset(identifier):
        """
        طلب إعادة تعيين كلمة المرور.
        
        Args:
            identifier: رقم الهاتف أو البريد الإلكتروني أو اسم المستخدم
        
        Returns:
            tuple: (success, message)
        """
        try:
            # البحث عن المورد
            clean_phone_suffix = str(identifier)[-9:] if str(identifier).isdigit() else identifier
            supplier = Supplier.query.filter(
                (Supplier.username == identifier) |
                (Supplier.email == identifier) |
                (Supplier.search_phone == clean_phone_suffix)
            ).first()

            if not supplier:
                return False, "المورد غير موجود"

            # إنشاء رمز OTP لإعادة التعيين
            otp_record, otp_code = OTP.create_otp(
                identifier=supplier.phone or supplier.email,
                target_id=supplier.id,
                target_type='supplier',
                expiry_seconds=300
            )

            return True, {
                "message": "تم إرسال رمز إعادة تعيين كلمة المرور",
                "otp_code": otp_code  # للتطوير فقط - احذفه في الإنتاج
            }

        except Exception as e:
            db.session.rollback()
            return False, f"خطأ في طلب إعادة التعيين: {str(e)}"

    @staticmethod
    def reset_password(identifier, otp_code, new_password):
        """
        إعادة تعيين كلمة المرور بعد التحقق من الرمز.
        
        Args:
            identifier: رقم الهاتف أو البريد الإلكتروني أو اسم المستخدم
            otp_code: رمز التحقق
            new_password: كلمة المرور الجديدة
        
        Returns:
            tuple: (success, message)
        """
        try:
            # البحث عن المورد
            clean_phone_suffix = str(identifier)[-9:] if str(identifier).isdigit() else identifier
            supplier = Supplier.query.filter(
                (Supplier.username == identifier) |
                (Supplier.email == identifier) |
                (Supplier.search_phone == clean_phone_suffix)
            ).first()

            if not supplier:
                return False, "المورد غير موجود"

            # التحقق من رمز OTP
            if otp_code != "123456":  # في الإنتاج: تحقق من قاعدة البيانات
                return False, "رمز التحقق غير صحيح"

            # تحديث كلمة المرور
            supplier.set_password(new_password)
            db.session.commit()

            return True, "تم تحديث كلمة المرور بنجاح"

        except Exception as e:
            db.session.rollback()
            return False, f"خطأ في تحديث كلمة المرور: {str(e)}"
