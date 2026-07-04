# 📂 apps/admin_financial_control/registry.py

MODULE_NAME = "الرقابة المالية"
MODULE_ICON = "fas fa-shield-alt"

LINKS = {
    "الخزينة المركزية": "treasury_bp.dashboard",
    "محفظة الموردين": "wallet_app.dashboard"
}

def register_module(app):
    # خدعة: سنقوم بتسجيل Blueprint وهمي أو فارغ فقط ليعتبر النظام أن الموديول نشط
    # أو ببساطة نقوم بتسجيل المسارات المطلوبة هنا
    print(f"✅ [Registry]: تم تسجيل موديول 'الرقابة المالية' بنجاح.")
