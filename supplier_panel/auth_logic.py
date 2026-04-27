from flask import session
from core.models import User, Supplier
from werkzeug.security import check_password_hash

def verify_supplier_credentials(username, password):
    """
    محرك التحقق السيادي المطور: 
    يقوم بالتحقق من الهوية عبر جدول المستخدمين المركزي ويربطها بملف المورد.
    """
    try:
        # 1. تنظيف المدخلات
        clean_username = username.strip() if username else ""
        
        # 2. البحث في جدول المستخدمين (المدخل المركزي)
        user = User.query.filter_by(username=clean_username).first()

        # 3. فحص الوجود والتأكد من "الدور" (Role)
        if not user:
            return '⚠️ هذا الاسم غير مسجل في سجلاتنا المركزية.', 'danger', None
        
        if user.role != 'supplier':
            return '⛔ عذراً، هذه البوابة مخصصة للموردين فقط.', 'danger', None

        # 4. مطابقة كلمة المرور باستخدام نظام التشفير (Hash)
        # نستخدم check_password_hash للأمان العالي
        if not check_password_hash(user.password, password.strip()):
            # ملاحظة: إذا كنت لا تزال تستخدم نصاً عادياً للتجربة، استبدلها بـ:
            # if user.password != password.strip():
            return '❌ كلمة المرور السيادية غير صحيحة.', 'warning', None

        # 5. جلب ملف المورد (الترسانة المالية) المرتبط بهذا المستخدم
        supplier = user.supplier_profile
        if not supplier:
            return '⚠️ الحساب مسجل ولكن لا يوجد ملف مورد مرتبظ به.', 'danger', None

        # 6. التوثيق (الختم الفوري وتطهير الجلسة)
        session.clear() 
        session.permanent = True
        session['user_type'] = 'supplier' 

        return f'✅ أهلاً بك يا {supplier.trade_name}.. تم فتح الترسانة.', 'success', user

    except Exception as e:
        print(f"❌ [Logic Error]: {e}")
        return f'⚠️ عطل فني في بوابة العبور: {str(e)}', 'danger', None
with app.app_context():
    # هذا السطر سيقوم بإنشاء الجداول التي لا تزال ناقصة في قاعدة البيانات
    db.create_all()
    print("✅ تم تحديث جداول قاعدة البيانات لتطابق الهيكل السيادي الجديد.")
