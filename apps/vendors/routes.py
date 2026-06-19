from . import vendors_manager # استيراد المدير الخاص بنا

@vendors_manager.route('/vendor/dashboard')
def dashboard():
    return "لوحة المورد الخاصة"
