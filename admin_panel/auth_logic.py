# admin_panel/auth_logic.py
from core.models.user import User
from flask_login import login_user

class AdminAuthLogic:
    @staticmethod
    def authenticate_admin(username, password):
        """المنطق السيادي للتحقق من هوية المدير"""
        user = User.query.filter_by(username=username).first()
        
        # 1. التحقق من وجود المستخدم
        if not user:
            return False, "⚠️ عذراً، هذا المستخدم غير مسجل في النظام.", None
            
        # 2. التحقق من كلمة المرور (تأكد من وجود دالة check_password في موديل User)
        if not user.check_password(password):
            return False, "❌ كلمة المرور غير صحيحة، حاول مجدداً.", None
            
        # 3. التحقق من الرتبة (يجب أن تكون admin)
        if getattr(user, 'role', '').lower() != 'admin':
            return False, "🚫 الوصول مرفوض: الحساب لا يملك صلاحيات إدارية.", None

        # 4. التحقق من حالة الحساب
        if not getattr(user, 'is_active_account', True):
            return False, "🔒 الحساب موقوف حالياً، يرجى مراجعة الدعم.", None
            
        # إذا اجتاز كل الاختبارات، يتم تسجيل الدخول
        login_user(user)
        return True, "تم فتح بوابة القيادة بنجاح.", user
