# coding: utf-8
# ملف التشغيل الرئيسي - منصة محجوب أونلاين
import os
import sys

# 1. تهيئة المسارات البرمجية
# نضمن أن النظام يرى مجلد apps كحزمة برمجية رئيسية
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 2. استيراد دالة مصنع التطبيق من مجلد apps
# ملاحظة: سيقوم هذا السطر بتنفيذ الكود الموجود في apps/__init__.py
try:
    from apps import create_app
    print("✅ تم استيراد محرك التطبيق من مجلد apps بنجاح")
except ImportError as e:
    print(f"❌ خطأ حرج: لم يتم العثور على حزمة apps. التفاصيل: {e}")
    sys.exit(1) # إغلاق التشغيل في حال فشل الاستيراد

# 3. إنشاء كائن التطبيق
# هذا المتغير 'app' هو ما يبحث عنه خادم Railway لتشغيل الموقع
app = create_app()

# 4. نقطة الانطلاق عند التشغيل محلياً
if __name__ == "__main__":
    # تشغيل التطبيق على المنفذ المخصص (أو 5000 افتراضياً)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
