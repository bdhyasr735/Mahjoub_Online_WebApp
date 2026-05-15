# coding: utf-8
# 🚀 محرك الإقلاع لمنصة محجوب أونلاين
import os
import sys
from apps import create_app, db

# التأكد من إضافة المسار الحالي للنظام لضمان رؤية حزمة apps
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

app = create_app()

if __name__ == "__main__":
    # استلام المنفذ (Port) ديناميكياً من Railway
    # إذا لم يجد متغير بيئة، سيستخدم 5000 كافتراضي للمعاينة المحلية
    port = int(os.environ.get("PORT", 5000))
    
    try:
        # تشغيل السيرفر على العنوان العام 0.0.0.0 ليتمكن Railway من توجيه الترافيك إليه
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"❌ فشل إقلاع المحرك: {e}")
