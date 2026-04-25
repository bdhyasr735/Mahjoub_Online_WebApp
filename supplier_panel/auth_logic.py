# التعديل: استيراد الموديل مباشرة من ملفه لضمان الاستقرار
from core.models.supplier import Supplier

def verify_supplier_credentials(username, password):
    """
    منطق التحقق الخاص بالمنصة اللامركزية لمحجوب أونلاين.
    هذا المحرك يفحص الهوية السيادية للمورد قبل السماح له بدخول الترسانة.
    إرجاع: (الرسالة، نوع التنبيه، كائن المورد أو None)
    """
    try:
        # 1. البحث عن المورد عبر "اسم الدخول" 
        # ملاحظة سيادية: تأكد أن حقل الاسم في قاعدة البيانات هو 'name' وليس 'username'
        supplier = Supplier.query.filter_by(name=username).first()

        # 2. فحص الوجود
        if not supplier:
            return '⚠️ عذراً، هذا الاسم غير مسجل في المنصة اللامركزية لمحجوب أونلاين.', 'danger', None

        # 3. فحص كلمة المرور
        # ملاحظة أمنية: لاحقاً سنستخدم check_password_hash للأمان العالي
        if str(supplier.password).strip() != str(password).strip():
            return '❌ كلمة المرور غير صحيحة، يرجى إعادة التثبت من مفاتيح الدخول.', 'warning', None

        # 4. النجاح المطلق
        return f'✅ مرحباً بك يا {supplier.name}.. تم التحقق من الهوية السيادية بنجاح.', 'success', supplier

    except Exception as e:
        # تسجيل الخطأ في السيرفر للمراجعة
        print(f"❌ [Logic Error] فشل في عملية التحقق السيادي: {e}")
        return f'⚠️ حدث خطأ تقني في نظام التحقق: {str(e)}', 'danger', None
