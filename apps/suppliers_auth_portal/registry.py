class SupplierPortalRegistry:
    @staticmethod
    def register_new_supplier(data):  # ✅ تسجيل مورد جديد + إنشاء محفظة
        ...
    
    @staticmethod
    def verify_supplier_otp(identifier, otp_code):  # ✅ التحقق من رمز OTP
        ...
    
    @staticmethod
    def resend_otp(identifier):  # ✅ إعادة إرسال الرمز
        ...
    
    @staticmethod
    def request_password_reset(identifier):  # ✅ طلب إعادة تعيين كلمة المرور
        ...
    
    @staticmethod
    def reset_password(identifier, otp_code, new_password):  # ✅ إعادة تعيين كلمة المرور
        ...
