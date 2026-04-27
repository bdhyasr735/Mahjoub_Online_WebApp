import os
import sys

# إجبار السيرفر على رؤية المجلد الحالي كحزمة
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import create_app

app = create_app()

if __name__ == "__main__":
    # تشغيل متوافق مع Railway
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
