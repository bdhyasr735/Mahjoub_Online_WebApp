import sys
import traceback
from apps import create_app

try:
    # محاولة تشغيل المصنع المركزي
    app = create_app()
    print("✅ المصنع المركزي للنواة يعمل بنجاح!")
except Exception:
    # في حال حدوث أي خطأ، سنقوم بطباعته في الـ Logs
    print("❌ فشل تشغيل المصنع المركزي، التفاصيل أدناه:")
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    app.run()
