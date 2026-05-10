# core/setup/auth_loaders.py
from core.extensions import login_manager
from core.models.user import User
from core.models.supplier import Supplier

@login_manager.user_loader
def load_user(user_id):
    """
    محرك استعادة الهوية (Multi-Entity Loader):
    يقوم بالتحقق من هوية المستخدم في كل من جداول المسؤولين والموردين
    """
    
    # التأكد من أن المعرف ليس فارغاً لتجنب أخطاء التحويل
    if user_id is None or user_id == 'None' or not str(user_id).isdigit():
        return None
    
    try:
        # 1. البحث أولاً في جدول المستخدمين (المدراء/الأدمن) - الأولوية للقيادة
        user = User.query.get(int(user_id))
        if user:
            return user
            
        # 2. إذا لم يتم العثور عليه، يتم البحث في جدول الموردين (Suppliers)
        # هذا يتيح للموردين تسجيل الدخول لحساباتهم الخاصة لاحقاً
        supplier = Supplier.query.get(int(user_id))
        if supplier:
            return supplier
            
    except Exception as e:
        # في حال حدوث خطأ مفاجئ في قاعدة البيانات، يتم إرجاع None لمنع انهيار السيرفر
        print(f"⚠️ خطأ في محرك استعادة الهوية: {e}")
        return None

    return None
