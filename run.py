# coding: utf-8
# 🚀 ملف التشغيل الرئيسي للنواة - محجوب أونلاين 2026
import os
import sys
import traceback
from apps import create_app

# تهيئة التطبيق عبر المصنع المركزي (Central Factory Pattern)
try:
    app = create_app()
    print("✅ المصنع المركزي للنواة يعمل بنجاح!")
except Exception:
    print("❌ فشل تشغيل المصنع المركزي، التفاصيل أدناه:")
    traceback.print_exc()
    # الخروج بكود 1 يخبر المنصات السحابية بوجود خطأ في التهيئة
    sys.exit(1)

# هذا الجزء يُنفذ فقط عند تشغيل الملف مباشرة (python run.py)
# ولا يؤثر على عمل gunicorn في الإنتاج (Production)
if __name__ == "__main__":
    # الحصول على المنفذ من متغيرات البيئة (Railway/Render يفرضان منفذًا خاصًا)
    # أو استخدام 5000 كقيمة افتراضية للتشغيل المحلي
    port = int(os.environ.get("PORT", 5000))
    
    # التشغيل على كافة الواجهات (0.0.0.0) لضمان الاستجابة لطلبات الشبكة
    # debug=False ضروري جداً لبيئات الإنتاج لأسباب أمنية
    app.run(host="0.0.0.0", port=port, debug=False)
