# coding: utf-8
# 🚨 [كود غرس مؤقت] لتنظيف الكاش وفحص الملفات قبل الإقلاع
import os
import shutil

print("🧹 [Bootstrapper - Clean] بدء إجبار السيرفر على حذف كاش بايثون المؤقت...")
for root, dirs, files in os.walk('.'):
    for d in dirs:
        if d == '__pycache__':
            path = os.path.join(root, d)
            try:
                shutil.rmtree(path)
                print(f"✅ تم مسح الكاش من المسار: {path}")
            except Exception as e:
                print(f"❌ فشل مسح كاش {path}: {e}")

print("🔍 [Bootstrapper - Inspect] قراءة الأسطر الأولى من wallet_db.py لقطع الشك باليقين:")
try:
    with open("apps/models/wallet_db.py", "r", encoding="utf-8") as f:
        lines = f.readlines()
        print("================== بداية ملف wallet_db.py في السيرفر حالياً ==================")
        for line in lines[:15]:  # طباعة أول 15 سطر فقط لتفقد الترتيب
            print(line.rstrip())
        print("==========================================================================")
except Exception as e:
    print(f"❌ تعذر قراءة ملف المحفظة للتحقق: {e}")


# ------------------------------------------------------------------
# 🟢 كود الإنتاج الخاص بك يبدأ من هنا (سيتم تنفيذه بعد التنظيف مباشرة)
# ------------------------------------------------------------------
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
    # تشغيل السيرفر
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
