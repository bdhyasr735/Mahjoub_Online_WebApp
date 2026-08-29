# apps/suppliers_auth_portal/registry.py
import uuid
from datetime import datetime

class SupplierPortalRegistry:
    """مسؤول عن إدارة عمليات التسجيل والتحقق وإنشاء المحافظ الوهمية أو المرتبطة بقاعدة البيانات"""
    
    @staticmethod
    def register_new_supplier(data):
        # محاكاة إنشاء سجل المورد والمحفظة المالية الذكية
        company_name = data.get('company_name')
        owner_name = data.get('owner_name')
        email = data.get('email')
        phone = data.get('phone')
        
        # توليد رقم حساب مالي فريد للمحفظة
        account_number = f"YE-SUPP-{uuid.uuid4().hex[:8].upper()}"
        
        supplier_record = {
            "id": uuid.uuid4().hex,
            "company_name": company_name,
            "category": data.get('category'),
            "full_address": data.get('full_address'),
            "owner_name": owner_name,
            "email": email,
            "phone": phone,
            "is_verified": False,
            "created_at": datetime.utcnow().isoformat(),
            "wallet": {
                "account_number": account_number,
                "balance": 0.0,
                "currency": "YER/SAR"
            },
            "employees": data.get('employees', [])
        }
        
        # هنا يتم الحفظ في قاعدة البيانات الفعلية (PostgreSQL / SQLAlchemy)
        return True, supplier_record

    @staticmethod
    def verify_supplier_otp(otp_code):
        # منطق التحقق من صحة رمز الـ OTP
        if otp_code == "123456" or len(otp_code) == 6:
            return True, "تم التحقق من الحساب وتفعيل المحفظة المالية بنجاح"
        return False, "رمز التحقق غير صحيح"
