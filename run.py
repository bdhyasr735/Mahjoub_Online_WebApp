import os
from core import create_app

# إنشاء نسخة التطبيق
app = create_app()

if __name__ == '__main__':
    # الحصول على المنفذ من بيئة Render أو استخدام 10000 كافتراضي
    port = int(os.environ.get("PORT", 10000))
    
    # تشغيل السيرفر مع تحديد المنفذ والمضيف (Host) ليكون متاحاً للإنترنت
    app.run(host='0.0.0.0', port=port, debug=False)
