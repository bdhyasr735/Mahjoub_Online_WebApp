# --- المحرك السيادي للتحقق من الهوية - محجوب أونلاين ---
from flask import session
from core.models.supplier import Supplier

def verify_supplier_credentials(username, password):
    """
    منطق التحقق الخاص بالمنصة اللامركزية لمحجوب أونلاين.
    هذا المحرك يفحص الهوية السيادية للمورد قبل السماح له بدخول الترسانة.
    
    المخرجات: (رسالة الحالة، صنف التنبيه، كائن المورد الموثق)
    """
    try:
        # 1. تطهير المدخلات (Data Sanitization)
        # نقوم بتنظيف الفراغات لضمان مطابقة دقيقة في قاعدة البيانات
        clean_username = username.strip() if username else ""
        
        # 2. الاستعلام عن الهوية
        # البحث يتم عبر حقل 'name' وهو المعرف السيادي للمورد في النظام
        supplier = Supplier.query.filter_by(name=clean_username).first()

        # 3. فحص الوجود (Existence Check)
        if not supplier:
            return '⚠️ عذراً، هذا الاسم غير مسجل في المنصة اللامركزية لمحجوب أونلاين.', 'danger', None

        # 4. مطابقة مفاتيح الدخول (Password Verification)
        # ملاحظة: يتم التحويل لنص لضمان عدم حدوث تعارض في الأنواع (Types)
        stored_password = str(supplier.password).strip() if supplier.password else ""
        provided_password = str(password).strip() if password else ""

        if stored_password != provided_password:
            return '❌ كلمة المرور غير صحيحة، يرجى إعادة التثبت من مفاتيح الدخول.', 'warning', None

        # 5. التوثيق وتحديد المسار (Sovereign Session Labeling)
        # قبل إتمام العملية، نخبر النظام أن صاحب هذه الجلسة هو "مورد" 
        # لضمان عدم تداخله مع حسابات الإدارة في ملف __init__.py
        session['user_type'] = 'supplier'

        # 6. النجاح المطلق
        return f'✅ مرحباً بك يا {supplier.name}.. تم التحقق من الهوية السيادية بنجاح.', 'success', supplier

    except Exception as e:
        # تسجيل العطل في مخرجات النظام (Terminal) للمراجعة الفنية
        print(f"❌ [Logic Error] فشل في عملية التحقق السيادي: {e}")
        return f'⚠️ حدث خطأ تقني في نظام التحقق: {str(e)}', 'danger', None
