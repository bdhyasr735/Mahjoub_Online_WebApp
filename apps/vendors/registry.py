# coding: utf-8
# 📂 apps/vendors/registry.py - البوابة السيادية للتسجيل الذاتي لمحرك الموردين

from .routes import vendors_bp 

def register_app(app):
    """
    دالة التسجيل الذاتي لتطبيق الموردين في المصنع الأم.
    تُستدعى تلقائياً من قبل المصنع المركزي (apps/__init__.py) لضمان العزل الحوكمي التام.
    """
    # 1️⃣ تسجيل مسارات الموردين تحت البادئة المعتمدة /vendors
    app.register_blueprint(vendors_bp, url_prefix='/vendors')
    
    # 2️⃣ إعدادات حوكمة الموردين المستقبلية (تُحقن هنا تلقائياً ليبقى المصنع الأم نظيفاً)
    @vendors_bp.app_context_processor
    def inject_vendor_branding():
        """حقن متغيرات الهوية البصرية (الملكية) للموردين في القوالب تلقائياً"""
        return {
            "VENDOR_PRIMARY_COLOR": "#4B0082",  # الأرجواني الملكي (Royal Purple)
            "VENDOR_ACCENT_COLOR": "#FFD700",   # الذهب الخالص (Gold)
            "PLATFORM_NAME": "MAHJOUB ONLINE"
        }

    # 3️⃣ معالجات الأخطاء الخاصة بنطاق الموردين (مثال للحوكمة الأمنيّة)
    @vendors_bp.app_errorhandler(403)
    def vendor_forbidden(error):
        return {"status": "error", "message": "صلاحيات سيادية غير كافية للوصول إلى هذا المحرك"}, 403

    print("👑 [MAHJOUB BRIDGE] تم ربط وتفعيل مصنع الموردين بنجاح عبر بوابة التسجيل الذاتي.")
