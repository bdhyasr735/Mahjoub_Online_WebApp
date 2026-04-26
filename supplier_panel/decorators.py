from functools import wraps
from flask import redirect, url_for, request
from flask_login import current_user
from core.models.supplier import Supplier # تأكد من استيراد موديل المورد بشكل صحيح

def sovereign_approval_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. التحقق من تسجيل الدخول
        if not current_user.is_authenticated:
            return redirect(url_for('supplier_panel.login'))

        # 2. كسر الكاش الرقمي: استعلام مباشر من قاعدة البيانات
        # هذا السطر يضمن أننا نقرأ الحالة الحالية "الآن" وليس ما هو مخزن في الجلسة
        fresh_supplier = Supplier.query.get(current_user.id)
        
        if not fresh_supplier or not fresh_supplier.is_approved:
            # منع التكرار اللانهائي: إذا لم يكن في صفحة الانتظار، أرسله إليها
            if request.endpoint != 'supplier_panel.waiting_room':
                return redirect(url_for('supplier_panel.waiting_room'))
        
        # إذا وصل الكود هنا وكان في صفحة الانتظار وهو معتمد أصلاً، 
        # سيقوم الـ routes بتوجيهه للداشبورد تلقائياً
        return f(*args, **kwargs)
    return decorated_function
