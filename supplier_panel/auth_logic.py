from core.models import Supplier

def verify_supplier_credentials(username, password):
    """
    منطق التحقق الخاص بالمنصة اللامركزية لمحجوب أونلاين
    إرجاع: (الرسالة، نوع التنبيه، كائن المورد أو None)
    """
    # 1. البحث عن المورد أولاً
    supplier = Supplier.query.filter_by(name=username).first()

    # 2. إذا كان الاسم غير موجود نهائياً
    if not supplier:
        return 'عذراً، هذا الاسم غير مسجل في المنصة اللامركزية.', 'danger', None

    # 3. إذا كان الاسم موجوداً ولكن كلمة المرور خاطئة
    if supplier.password != password:
        return 'كلمة المرور غير صحيحة، يرجى إعادة التثبت.', 'warning', None

    # 4. النجاح في التحقق
    return f'مرحباً بك يا {supplier.name}.. تم التحقق بنجاح.', 'success', supplier
