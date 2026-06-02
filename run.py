# run.py المحسّن للإنتاج مع محرك بناء الجداول التلقائي
import os
from apps import create_app
from apps.extensions import db

# إنشاء التطبيق
app = create_app()

# محرك البناء التلقائي (يضمن وجود الجداول قبل بدء السيرفر)
with app.app_context():
    try:
        db.create_all()
        print("✅ [Bootstrapper] تم فحص وبناء جداول قاعدة البيانات بنجاح.")
    except Exception as e:
        print(f"❌ [Bootstrapper] خطأ أثناء بناء الجداول: {e}")

if __name__ == "__main__":
    # تشغيل السيرفر (محلياً أو في الإنتاج)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False) # تم ضبط debug إلى False للإنتاج
