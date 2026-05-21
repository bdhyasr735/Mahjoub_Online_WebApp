# coding: utf-8
import os
import sys
import traceback
from apps import create_app

# تهيئة التطبيق عبر المصنع المركزي
try:
    app = create_app()
    print("✅ المصنع المركزي للنواة يعمل بنجاح!")
except Exception:
    print("❌ فشل تشغيل المصنع المركزي، التفاصيل أدناه:")
    traceback.print_exc()
    # الخروج بكود 1 يخبر المنصات أن هناك خطأ في التهيئة (ضروري لـ Render)
    sys.exit(1)

# هذا الجزء مخصص للتشغيل المحلي أو للتوافق مع سيرفرات الـ WSGI
if __name__ == "__main__":
    # الحصول على المنفذ من متغيرات البيئة (Render يفرض منفذًا خاصًا)
    # أو استخدام 5000 كقيمة افتراضية للتشغيل المحلي
    port = int(os.environ.get("PORT", 5000))
    
    # التشغيل على كافة الواجهات (0.0.0.0) لضمان الوصول من المنصات الخارجية
    app.run(host="0.0.0.0", port=port, debug=False)
