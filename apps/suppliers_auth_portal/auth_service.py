# coding: utf-8
# 📂 apps/suppliers_auth_portal/auth_service.py - تم التعطيل (Disabled)

class VendorAuthService:
    @staticmethod
    def initiate_login(phone, otp_code=None, retries=3):
        """
        تم تعطيل خدمة إرسال الرموز عبر HyperSender.
        النظام الآن يعتمد على التحقق المباشر (كلمة المرور).
        """
        print(f"INFO: VendorAuthService is disabled. Request for {phone} skipped.")
        return False
