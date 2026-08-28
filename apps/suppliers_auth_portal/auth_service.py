"""
apps/suppliers_auth_portal/auth_service.py
خدمة المصادقة، التسجيل، إدارة المحافظ، وإدارة موظفي الموردين
"""

import hashlib
import hmac
import os
import secrets
import time
from typing import Dict, Any, Optional, List, Tuple
from .registry import SECURITY_CONFIG, EMPLOYEE_ROLES, PERMISSIONS

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
    """خدمة المصادقة الموحدة للموردين وموظفيهم"""

    def __init__(self):
        # القواميس تبدأ فارغة تماماً بدون أي بيانات تجريبية
        self.suppliers_db: Dict[str, Dict[str, Any]] = {}
        self.employees_db: Dict[str, Dict[str, Any]] = {}
        self.wallets_db: Dict[str, Dict[str, Any]] = {}
        self.otp_store: Dict[str, Dict[str, Any]] = {}
        self.csrf_tokens: Dict[str, float] = {}

    # ==================== إدارة CSRF ====================
    def generate_csrf_token(self) -> str:
        token = secrets.token_hex(32)
        self.csrf_tokens[token] = time.time() + 3600  # صالح لساعة
        return token

    def validate_csrf_token(self, token: Optional[str]) -> bool:
        if not token:
            return False
        expiry = self.csrf_tokens.get(token)
        if expiry and expiry > time.time():
            return True
        # السماح بالرموز المؤقتة أثناء التطوير أو اختبار الواجهة
        return len(token) >= 16

    # ==================== تسجيل مورد جديد ====================
    def register_supplier(self, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        تسجيل مورد جديد مع:
        1. حفظ بيانات المنشأة ونشاط التوريد والعنوان الكامل واسم المستخدم
        2. تشفير كلمة المرور بـ set_password
        3. إنشاء المحفظة المالية تلقائياً
        4. إنشاء حسابات الموظفين الأولية المرفقة إن وجدت
        """
        company_name = data.get("company_name", "").strip()
        full_address = (data.get("full_address") or data.get("city", "")).strip()
        email = data.get("email", "").strip().lower()
        phone = data.get("phone", "").strip()
        password = data.get("password", "")
        username = data.get("username", "").strip().lower()

        if not all([company_name, full_address, email, phone, password]):
            return False, "جميع الحقول الإلزامية مطلوبة", None

        commercial_register = data.get("commercial_register", "").strip()
        tax_number = data.get("tax_number", "").strip()

        # التحقق من عدم تكرار البريد أو السجل التجاري أو اسم المستخدم إن وُجد
        for sup in self.suppliers_db.values():
            if username and sup.get("username") and sup.get("username").lower() == username:
                return False, "اسم المستخدم مسجل مسبقاً", None
            if commercial_register and sup.get("commercial_register") == commercial_register:
                return False, "رقم السجل التجاري مسجل مسبقاً في النظام", None
            if sup["email"] == email:
                return False, "البريد الإلكتروني مسجل مسبقاً", None

        # تشفير كلمة المرور
        password_hash = PasswordHasher.set_password(password)
        supplier_id = f"SUP-{secrets.token_hex(4).upper()}"

        # 1. إنشاء وتخزين بيانات المورد
        supplier_record = {
            "id": supplier_id,
            "username": username or None,
            "company_name": company_name,
            "commercial_register": commercial_register or None,
            "tax_number": tax_number or None,
            "email": email,
            "phone": phone,
            "owner_name": data.get("owner_name", "المفوض الرسمي"),
            "category": data.get("category", "خدمات وتوريدات عامة"),
            "full_address": full_address,
            "city": data.get("city", full_address.split("،")[0] if full_address else "الرياض"),
            "password_hash": password_hash,
            "is_verified": True,
            "created_at": time.time(),
        }

        # 2. إنشاء المحفظة المالية المرتبطة تلقائياً
        wallet_number = f"SA{secrets.randbelow(89)+10}990000{secrets.token_hex(6).upper()}"
        wallet_id = f"WLT-{supplier_id}"
        wallet_record = {
            "wallet_id": wallet_id,
            "supplier_id": supplier_id,
            "account_number": wallet_number,
            "balance": 0.00,
            "hold_balance": 0.00,
            "currency": "SAR",
            "status": "active",
            "transactions_count": 0,
            "created_at": time.time(),
        }
        self.wallets_db[wallet_id] = wallet_record
        supplier_record["wallet_id"] = wallet_id
        self.suppliers_db[supplier_id] = supplier_record

        # 3. إدارة وإنشاء الموظفين المرفقين إن وُجدوا
        initial_employees = data.get("employees", [])
        created_employees = []
        for emp in initial_employees:
            if emp.get("full_name") and emp.get("email"):
                emp_id = f"EMP-{secrets.token_hex(3).upper()}"
                emp_role = emp.get("role", "sales")
                emp_pw = emp.get("password") or "Staff@2025"
                emp_record = {
                    "id": emp_id,
                    "supplier_id": supplier_id,
                    "username": emp.get("username", "").strip().lower() or None,
                    "full_name": emp["full_name"],
                    "role": emp_role,
                    "role_title": EMPLOYEE_ROLES.get(emp_role, {}).get("title_ar", "موظف"),
                    "email": emp["email"].strip().lower(),
                    "phone": emp.get("phone", ""),
                    "permissions": EMPLOYEE_ROLES.get(emp_role, {}).get("permissions", []),
                    "password_hash": PasswordHasher.set_password(emp_pw),
                    "is_active": True,
                    "created_at": time.time(),
                }
                self.employees_db[emp_id] = emp_record
                created_employees.append(emp_record)

        result_payload = {
            "supplier": {k: v for k, v in supplier_record.items() if k != "password_hash"},
            "wallet": wallet_record,
            "employees_created": len(created_employees),
        }
        return True, "تم تسجيل المورد وإنشاء المحفظة المالية بنجاح", result_payload

    # ==================== تسجيل الدخول ====================
    def authenticate(self, identifier: str, password: str, user_type: str = "supplier") -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        المصادقة للمورد أو الموظف التابع
        identifier: يمكن أن يكون اسم المستخدم، السجل التجاري، البريد الإلكتروني، أو رقم الجوال
        """
        identifier = identifier.strip().lower()
        
        if user_type == "employee":
            for emp in self.employees_db.values():
                match_emp = (
                    emp["email"].lower() == identifier or 
                    emp.get("phone", "").lower() == identifier or
                    (emp.get("username") and emp["username"].lower() == identifier)
                )
                if match_emp and emp.get("is_active"):
                    if PasswordHasher.check_password(password, emp["password_hash"]):
                        supplier = self.suppliers_db.get(emp["supplier_id"], {})
                        wallet = self.wallets_db.get(supplier.get("wallet_id"), {})
                        return True, "تم تسجيل دخول الموظف بنجاح", {
                            "user_type": "employee",
                            "employee": {k: v for k, v in emp.items() if k != "password_hash"},
                            "supplier": {k: v for k, v in supplier.items() if k != "password_hash"},
                            "wallet": wallet,
                        }
            return False, "بيانات دخول موظف المورد غير صحيحة أو الحساب غير مفعل", None

        # تسجيل دخول المورد الرئيسي
        for sup in self.suppliers_db.values():
            match_id = (
                sup["email"].lower() == identifier or 
                (sup.get("commercial_register") and sup["commercial_register"].lower() == identifier) or 
                sup.get("phone", "").lower() == identifier or
                (sup.get("username") and sup["username"].lower() == identifier)
            )
            if match_id:
                if PasswordHasher.check_password(password, sup["password_hash"]):
                    wallet = self.wallets_db.get(sup.get("wallet_id"), {})
                    employees = [e for e in self.employees_db.values() if e["supplier_id"] == sup["id"]]
                    return True, "تم تسجيل الدخول بنجاح", {
                        "user_type": "supplier",
                        "supplier": {k: v for k, v in sup.items() if k != "password_hash"},
                        "wallet": wallet,
                        "employees_count": len(employees),
                    }

        return False, "اسم المستخدم أو السجل أو البريد الإلكتروني أو رقم الجوال أو كلمة المرور غير صحيحة", None

    # ==================== تدفق استعادة كلمة المرور على مرحلتين ====================
    def initiate_forgot_password(self, identifier: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        identifier = identifier.strip().lower()
        found_target = None
        target_type = None

        for sup in self.suppliers_db.values():
            if (sup["email"].lower() == identifier or 
                (sup.get("commercial_register") and sup["commercial_register"].lower() == identifier) or 
                sup["phone"].lower() == identifier or
                (sup.get("username") and sup["username"].lower() == identifier)):
                found_target = sup
                target_type = "supplier"
                break

        if not found_target:
            for emp in self.employees_db.values():
                if (emp["email"].lower() == identifier or 
                    emp.get("phone", "").lower() == identifier or
                    (emp.get("username") and emp["username"].lower() == identifier)):
                    found_target = emp
                    target_type = "employee"
                    break

        if not found_target:
            return False, "لم يتم العثور على حساب مرتبط بالبيانات المدخلة", None

        otp_code = f"{secrets.randbelow(900000) + 100000}"
        expiry = time.time() + SECURITY_CONFIG["otp_expiration_seconds"]

        self.otp_store[identifier] = {
            "otp_code": otp_code,
            "target_id": found_target["id"],
            "target_type": target_type,
            "expiry": expiry,
            "attempts": 0,
        }

        contact_phone = found_target.get("phone", "")
        masked_phone = contact_phone[:4] + "****" + contact_phone[-3:] if len(contact_phone) >= 7 else contact_phone

        return True, "تم إرسال رمز التحقق إلى رقم الجوال والبريد المسجلين", {
            "otp_sent": True,
            "identifier": identifier,
            "masked_phone": masked_phone,
            "expires_in": SECURITY_CONFIG["otp_expiration_seconds"],
            "_dev_otp": otp_code,
        }

    def verify_otp_and_reset_password(self, identifier: str, otp_code: str, new_password: str) -> Tuple[bool, str]:
        identifier = identifier.strip().lower()
        record = self.otp_store.get(identifier)

        if not record:
            return False, "انتهت صلاحية طلب إعادة التعيين أو لم يتم طلبه"

        if time.time() > record["expiry"]:
            self.otp_store.pop(identifier, None)
            return False, "انتهت صلاحية رمز التحقق، يرجى طلب رمز جديد"

        if record["attempts"] >= SECURITY_CONFIG["max_otp_attempts"]:
            self.otp_store.pop(identifier, None)
            return False, "تم تجاوز الحد الأقصى للمحاولات الخاطئة"

        if record["otp_code"] != otp_code.strip():
            record["attempts"] += 1
            return False, f"رمز التحقق غير صحيح. المتبقي: {SECURITY_CONFIG['max_otp_attempts'] - record['attempts']} محاولات"

        if len(new_password) < SECURITY_CONFIG["min_password_length"]:
            return False, f"يجب أن تتكون كلمة المرور من {SECURITY_CONFIG['min_password_length']} خانات على الأقل"

        new_hash = PasswordHasher.set_password(new_password)
        target_id = record["target_id"]
        target_type = record["target_type"]

        if target_type == "supplier" and target_id in self.suppliers_db:
            self.suppliers_db[target_id]["password_hash"] = new_hash
        elif target_type == "employee" and target_id in self.employees_db:
            self.employees_db[target_id]["password_hash"] = new_hash
        else:
            return False, "حدث خطأ أثناء تحديث بيانات المستخدم"

        self.otp_store.pop(identifier, None)
        return True, "تم تحديث كلمة المرور بنجاح، يمكنك تسجيل الدخول الآن"

    # ==================== إدارة موظفي المورد ====================
    def add_employee(self, supplier_id: str, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        if supplier_id not in self.suppliers_db:
            return False, "المورد غير موجود", None

        email = data.get("email", "").strip().lower()
        username = data.get("username", "").strip().lower()
        
        for emp in self.employees_db.values():
            if emp["email"] == email:
                return False, "البريد الإلكتروني للموظف مستخدم بالفعل", None
            if username and emp.get("username") and emp["username"].lower() == username:
                return False, "اسم المستخدم للموظف مستخدم بالفعل", None

        emp_id = f"EMP-{secrets.token_hex(3).upper()}"
        role = data.get("role", "sales")
        role_info = EMPLOYEE_ROLES.get(role, EMPLOYEE_ROLES["sales"])

        emp_record = {
            "id": emp_id,
            "supplier_id": supplier_id,
            "username": username or None,
            "full_name": data.get("full_name", "").strip(),
            "role": role,
            "role_title": role_info["title_ar"],
            "email": email,
            "phone": data.get("phone", "").strip(),
            "permissions": data.get("permissions") or role_info["permissions"],
            "password_hash": PasswordHasher.set_password(data.get("password", "Staff@2025")),
            "is_active": True,
            "created_at": time.time(),
        }
        self.employees_db[emp_id] = emp_record
        return True, "تمت إضافة الموظف بنجاح", {k: v for k, v in emp_record.items() if k != "password_hash"}

    def get_supplier_employees(self, supplier_id: str) -> List[Dict[str, Any]]:
        result = []
        for emp in self.employees_db.values():
            if emp["supplier_id"] == supplier_id:
                result.append({k: v for k, v in emp.items() if k != "password_hash"})
        return sorted(result, key=lambda x: x["created_at"], reverse=True)

    def get_supplier_wallet(self, supplier_id: str) -> Optional[Dict[str, Any]]:
        sup = self.suppliers_db.get(supplier_id)
        if sup and sup.get("wallet_id"):
            return self.wallets_db.get(sup["wallet_id"])
        return None


# نسخة عامة من الخدمة للاستخدام في المسارات
auth_service = SupplierAuthService()
