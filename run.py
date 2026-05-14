# coding: utf-8
# 🛡️ ملف التشغيل السيادي لمنصة محجوب أونلاين
# التوثيق: هذا الملف هو بوابة الدخول الرئيسية للخادم السحابي

import os
import sys

# 1. تهيئة مسارات النظام (System Paths)
# نضمن أن المحرك يرى مجلد 'apps' كحزمة رئيسية لضمان صحة الاستيراد
base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, base_dir)

try:
    # 2. استيراد دالة مصنع التطبيق من مجلد apps
    # هذا السطر يربط ملف التشغيل بكافة الإعدادات والدروع الموجودة في apps/__init__.py
    from apps import create_app
    
    # إنشاء كائن التطبيق
    app = create_app()
    
    print("✅ تم تشغيل محرك منصة محجوب أونلاين بنجاح")

except ImportError as e:
    print(f"❌ خطأ حرج: تعذر العثور على حزمة 'apps'. تأكد من وجود ملف __init__.py داخل المجلد. التفاصيل: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ حدث خطأ غير متوقع أثناء بدء التشغيل: {e}")
    sys.exit(1)

# 3. إعدادات التشغيل (للمحيط المحلي والسحابي)
if __name__ == "__main__":
    # الحصول على المنفذ من إعدادات Railway أو استخدام 5000 كافتراضي
    port = int(os.environ.get("PORT", 5000))
    
    # تشغيل التطبيق (host='0.0.0.0' ضروري لبيئات السحاب)
    app.run(host='0.0.0.0', port=port, debug=False)
