# 📂 run.py - النسخة الأكثر استقراراً
from apps import create_app
import os

# تهيئة التطبيق
app = create_app()

if __name__ == "__main__":
    # هذا التشغيل المحلي فقط
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
