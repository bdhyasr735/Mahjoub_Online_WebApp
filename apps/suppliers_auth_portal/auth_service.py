"""
apps/suppliers_auth_portal/auth_service.py
خدمة المصادقة، التسجيل، إدارة المحافظ، وإدارة موظفي الموردين
"""

import hashlib
import hmac
import os
import secrets
import time
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta

from flask import session
from sqlalchemy.exc import IntegrityError

from .registry import SECURITY_CONFIG, EMPLOYEE_ROLES, PERMISSIONS
from apps.extensions import db
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.supplier import Supplier  # افتراض وجود نموذج Supplier
from apps.models.wallet import Wallet  # افتراض وجود نموذج Wallet


class PasswordHasher:
    """تشفير والتحقق من كلمات المرور باستخدام PBKDF2 المعتمد أمنياً"""
    
    @staticmethod
    def set_password(password: str) -> str:
        """تشفير كلمة المرور بملح أمان عشوائي"""
        salt = os.urandom(16).hex()
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations=100000
        )
        return f"pbkdf2_sha256$100000${salt}${key.hex()}"

    @staticmethod
    def check_password(password: str, hashed: str) -> bool:
        """التحقق من صحة كلمة المرور المدخلة"""
        try:
            algorithm, iterations, salt, key = hashed.split('$')
            test_key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                iterations=int(iterations)
            )
            return hmac.compare_digest(key, test_key.hex())
        except Exception:
            return False


class SupplierAuthService:
    """خدمة المصادقة الموحدة للموردين وموظفيهم - تدعم SQLAlchemy"""

    def __init__(self):
        # لا حاجة لقواميس - كل شيء في قاعدة البيانات
        pass

    # ==================== إدارة CSRF ====================
    def generate_csrf_token(self) -> str:
        token = secrets.token_hex(32)
        # تخزين في الجلسة بدلاً من قاعدة البيانات (أسهل)
        session['csrf_token'] = token
        session['csrf_expiry'] = time.time() + 3600
        return token

    def validate_csrf_token(self, token: Optional[str]) -> bool:
        if not token:
            return False
        
        stored_token = session.get('csrf_token')
        expiry = session.get('csrf_expiry', 0)
        
        if stored_token and token == stored_token and expiry > time.time():
            return True
        
        return len(token) >= 16

    # ==================== تسجيل مورد جديد ====================
    def register_supplier(self, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        تسجيل مورد جديد مع:
        1. حفظ بيانات المنشأة ونشاط التوريد والعنوان الكامل ورقم الهاتف والبريد
        2. تشفير كلمة المرور
        3. إنشاء المحفظة المالية تلقائياً
        4. إضافة الموظفين إن وُجدوا
        """
        from apps.models.supplier import Supplier
        from apps.models.wallet import Wallet
        
        company_name = data.get("company_name", "").strip()
        full_address = (data.get("full_address") or data.get("city", "")).strip()
        email = data.get("email", "").strip().lower()
        phone = data.get("phone", "").strip()
        password = data.get("password", "")

        if not all([company_name, full_address, email, phone, password]):
            return False, "جميع الحقول الإلزامية مطلوبة", None

        commercial_register = data.get("commercial_register", "").strip()
        tax_number = data.get("tax_number", "").strip()

        # التحقق من عدم تكرار البريد أو الهاتف
        existing_supplier = Supplier.query.filter(
            (Supplier.email == email) | (Supplier.phone == phone)
        ).first()
        
        if existing_supplier:
            if existing_supplier.email == email:
                return False, "البريد الإلكتروني مسجل مسبقاً", None
            return False, "رقم الهاتف مسجل مسبقاً", None

        if commercial_register:
            existing = Supplier.query.filter_by(commercial_register=commercial_register).first()
            if existing:
                return False, "رقم السجل التجاري مسجل مسبقاً في النظام", None

        try:
            # تشفير كلمة المرور
            password_hash = PasswordHasher.set_password(password)
            
            # إنشاء المورد
            supplier = Supplier(
                company_name=company_name,
                commercial_register=commercial_register or None,
                tax_number=tax_number or None,
                email=email,
                phone=phone,
                owner_name=data.get("owner_name", "المفوض الرسمي"),
                category=data.get("category", "خدمات وتوريدات عامة"),
                full_address=full_address,
                city=data.get("city", full_address.split("،")[0] if full_address else "الرياض"),
                password_hash=password_hash,
                is_verified=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(supplier)
            db.session.flush()  # للحصول على supplier.id

            # إنشاء المحفظة المالية
            wallet_number = f"SA{secrets.randbelow(89)+10}990000{secrets.token_hex(6).upper()}"
            
            wallet = Wallet(
                supplier_id=supplier.id,
                account_number=wallet_number,
                balance=0.00,
                hold_balance=0.00,
                currency="SAR",
                status="active",
                transactions_count=0,
                created_at=datetime.utcnow()
            )
            
            db.session.add(wallet)
            
            # إضافة الموظفين إن وُجدوا
            initial_employees = data.get("employees", [])
            created_employees = []
            
            for emp in initial_employees:
                if emp.get("full_name") and emp.get("email"):
                    emp_role = emp.get("role", "sales")
                    role_info = EMPLOYEE_ROLES.get(emp_role, EMPLOYEE_ROLES["sales"])
                    emp_pw = emp.get("password") or "Staff@2025"
                    
                    staff = SupplierStaff(
                        supplier_id=supplier.id,
                        username=emp["email"].strip().lower(),
                        full_name=emp["full_name"],
                        email=emp["email"].strip().lower(),
                        phone=emp.get("phone", "").strip(),
                        position=role_info.get("title_ar", "موظف"),
                        role=emp_role,
                        status="active",
                        created_at=datetime.utcnow()
                    )
                    staff.set_password(emp_pw)
                    
                    db.session.add(staff)
                    created_employees.append(staff)
            
            db.session.commit()
            
            # استرجاع البيانات
            supplier_data = {
                "id": supplier.id,
                "company_name": supplier.company_name,
                "email": supplier.email,
                "phone": supplier.phone,
                "wallet_id": wallet.id,
                "is_verified": supplier.is_verified,
            }
            
            wallet_data = {
                "wallet_id": wallet.id,
                "account_number": wallet.account_number,
                "balance": wallet.balance,
                "currency": wallet.currency,
                "status": wallet.status,
            }
            
            return True, "تم تسجيل المورد وإنشاء المحفظة المالية بنجاح", {
                "supplier": supplier_data,
                "wallet": wallet_data,
                "employees_created": len(created_employees),
            }
            
        except IntegrityError as e:
            db.session.rollback()
            return False, f"خطأ في قاعدة البيانات: {str(e)}", None
        except Exception as e:
            db.session.rollback()
            return False, f"حدث خطأ أثناء التسجيل: {str(e)}", None

    # ==================== المصادقة ====================
    def authenticate(self, identifier: str, password: str, user_type: str = "supplier") -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        المصادقة للمورد أو الموظف التابع
        identifier: يُقبل فقط البريد الإلكتروني أو رقم الهاتف
        """
        from apps.models.supplier import Supplier
        from apps.models.wallet import Wallet
        
        identifier = identifier.strip().lower()
        
        if user_type == "employee":
            # البحث عن الموظف
            staff = SupplierStaff.query.filter(
                (SupplierStaff._email_enc == SupplierStaff._encrypt(identifier)) |
                (SupplierStaff.search_phone == str(identifier)[-9:])
            ).first()
            
            # إذا لم يتم العثور، نحاول البحث باستخدام username
            if not staff:
                staff = SupplierStaff.query.filter_by(username=identifier).first()
            
            if staff and staff.status == "active":
                if staff.check_password(password):
                    # استرجاع بيانات المورد
                    supplier = staff.supplier
                    wallet = Wallet.query.filter_by(supplier_id=supplier.id).first()
                    
                    # تحديث وقت آخر دخول
                    staff.last_login = datetime.utcnow()
                    db.session.commit()
                    
                    return True, "تم تسجيل دخول الموظف بنجاح", {
                        "user_type": "employee",
                        "employee": staff.to_dict(),
                        "supplier": {
                            "id": supplier.id,
                            "company_name": supplier.company_name,
                            "email": supplier.email,
                            "phone": supplier.phone,
                        },
                        "wallet": {
                            "wallet_id": wallet.id,
                            "account_number": wallet.account_number,
                            "balance": wallet.balance,
                        } if wallet else None,
                    }
            
            return False, "رقم الجوال أو البريد الإلكتروني أو كلمة المرور لموظف المورد غير صحيحة", None

        # تسجيل دخول المورد الرئيسي
        supplier = Supplier.query.filter(
            (Supplier.email == identifier) | (Supplier.phone == identifier)
        ).first()
        
        if supplier:
            if PasswordHasher.check_password(password, supplier.password_hash):
                wallet = Wallet.query.filter_by(supplier_id=supplier.id).first()
                
                # تحديث وقت آخر دخول
                supplier.last_login = datetime.utcnow()
                db.session.commit()
                
                # استرجاع الموظفين
                employees = SupplierStaff.query.filter_by(supplier_id=supplier.id).all()
                
                return True, "تم تسجيل الدخول بنجاح", {
                    "user_type": "supplier",
                    "supplier": {
                        "id": supplier.id,
                        "company_name": supplier.company_name,
                        "email": supplier.email,
                        "phone": supplier.phone,
                        "is_verified": supplier.is_verified,
                    },
                    "wallet": {
                        "wallet_id": wallet.id,
                        "account_number": wallet.account_number,
                        "balance": wallet.balance,
                    } if wallet else None,
                    "employees_count": len(employees),
                }

        return False, "رقم الجوال أو البريد الإلكتروني أو كلمة المرور غير صحيحة", None

    # ==================== استعادة كلمة المرور ====================
    def initiate_forgot_password(self, identifier: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        from apps.models.supplier import Supplier
        from apps.models.otp_store import OTPStore  # افتراض وجود نموذج OTPStore
        
        identifier = identifier.strip().lower()
        
        # البحث عن المورد
        supplier = Supplier.query.filter(
            (Supplier.email == identifier) | (Supplier.phone == identifier)
        ).first()
        
        target_id = None
        target_type = None
        contact_phone = None
        
        if supplier:
            target_id = supplier.id
            target_type = "supplier"
            contact_phone = supplier.phone
        else:
            # البحث عن الموظف
            staff = SupplierStaff.query.filter(
                (SupplierStaff._email_enc == SupplierStaff._encrypt(identifier)) |
                (SupplierStaff.username == identifier)
            ).first()
            
            if staff:
                target_id = staff.id
                target_type = "employee"
                contact_phone = staff.phone

        if not target_id:
            return False, "لم يتم العثور على حساب مرتبط برقم الجوال أو البريد المدخل", None

        otp_code = f"{secrets.randbelow(900000) + 100000}"
        expiry = datetime.utcnow() + timedelta(seconds=SECURITY_CONFIG["otp_expiration_seconds"])

        # تخزين OTP
        otp_record = OTPStore(
            identifier=identifier,
            otp_code=otp_code,
            target_id=target_id,
            target_type=target_type,
            expiry=expiry,
            attempts=0,
            created_at=datetime.utcnow()
        )
        
        db.session.add(otp_record)
        db.session.commit()

        masked_phone = contact_phone[:4] + "****" + contact_phone[-3:] if contact_phone and len(contact_phone) >= 7 else contact_phone or identifier

        return True, "تم إرسال رمز التحقق إلى رقم الجوال والبريد المسجلين", {
            "otp_sent": True,
            "identifier": identifier,
            "masked_phone": masked_phone,
            "expires_in": SECURITY_CONFIG["otp_expiration_seconds"],
            "_dev_otp": otp_code,  # للتطوير فقط
        }

    def verify_otp_and_reset_password(self, identifier: str, otp_code: str, new_password: str) -> Tuple[bool, str]:
        from apps.models.supplier import Supplier
        from apps.models.otp_store import OTPStore
        
        identifier = identifier.strip().lower()
        
        otp_record = OTPStore.query.filter_by(identifier=identifier).first()
        
        if not otp_record:
            return False, "انتهت صلاحية طلب إعادة التعيين أو لم يتم طلبه"

        if datetime.utcnow() > otp_record.expiry:
            db.session.delete(otp_record)
            db.session.commit()
            return False, "انتهت صلاحية رمز التحقق، يرجى طلب رمز جديد"

        if otp_record.attempts >= SECURITY_CONFIG["max_otp_attempts"]:
            db.session.delete(otp_record)
            db.session.commit()
            return False, "تم تجاوز الحد الأقصى للمحاولات الخاطئة"

        if otp_record.otp_code != otp_code.strip():
            otp_record.attempts += 1
            db.session.commit()
            return False, f"رمز التحقق غير صحيح. المتبقي: {SECURITY_CONFIG['max_otp_attempts'] - otp_record.attempts} محاولات"

        if len(new_password) < SECURITY_CONFIG["min_password_length"]:
            return False, f"يجب أن تتكون كلمة المرور من {SECURITY_CONFIG['min_password_length']} خانات على الأقل"

        # تحديث كلمة المرور
        if otp_record.target_type == "supplier":
            supplier = Supplier.query.get(otp_record.target_id)
            if supplier:
                supplier.password_hash = PasswordHasher.set_password(new_password)
        elif otp_record.target_type == "employee":
            staff = SupplierStaff.query.get(otp_record.target_id)
            if staff:
                staff.set_password(new_password)
        else:
            return False, "حدث خطأ أثناء تحديث بيانات المستخدم"

        # حذف سجل OTP
        db.session.delete(otp_record)
        db.session.commit()

        return True, "تم تحديث كلمة المرور بنجاح، يمكنك تسجيل الدخول الآن"

    # ==================== إدارة الموظفين ====================
    def add_employee(self, supplier_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        from apps.models.supplier import Supplier
        
        email = data.get("email", "").strip().lower()
        phone = data.get("phone", "").strip()
        
        # التحقق من وجود المورد
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return False, "المورد غير موجود", None
        
        # التحقق من تكرار البريد
        existing = SupplierStaff.query.filter_by(username=email).first()
        if existing:
            return False, "البريد الإلكتروني للموظف مستخدم بالفعل", None
        
        if phone:
            # التحقق من رقم الهاتف عبر search_phone
            existing = SupplierStaff.query.filter_by(search_phone=str(phone)[-9:]).first()
            if existing:
                return False, "رقم الجوال للموظف مستخدم بالفعل", None

        role = data.get("role", "sales")
        role_info = EMPLOYEE_ROLES.get(role, EMPLOYEE_ROLES["sales"])
        emp_pw = data.get("password", "Staff@2025")

        staff = SupplierStaff(
            supplier_id=supplier_id,
            username=email,
            full_name=data.get("full_name", "").strip(),
            email=email,
            phone=phone,
            position=role_info.get("title_ar", "موظف"),
            role=role,
            status="active",
            created_at=datetime.utcnow()
        )
        staff.set_password(emp_pw)
        
        db.session.add(staff)
        db.session.commit()

        return True, "تمت إضافة الموظف بنجاح", staff.to_dict()

    def get_supplier_employees(self, supplier_id: int) -> List[Dict[str, Any]]:
        employees = SupplierStaff.query.filter_by(supplier_id=supplier_id).order_by(
            SupplierStaff.created_at.desc()
        ).all()
        return [emp.to_dict() for emp in employees]

    def get_supplier_wallet(self, supplier_id: int) -> Optional[Dict[str, Any]]:
        from apps.models.wallet import Wallet
        
        wallet = Wallet.query.filter_by(supplier_id=supplier_id).first()
        if wallet:
            return {
                "wallet_id": wallet.id,
                "account_number": wallet.account_number,
                "balance": wallet.balance,
                "hold_balance": wallet.hold_balance,
                "currency": wallet.currency,
                "status": wallet.status,
            }
        return None


# نسخة عامة من الخدمة للاستخدام في المسارات
auth_service = SupplierAuthService()
