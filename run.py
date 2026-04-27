import os
import sys

# إجبار بايثون على رؤية المجلدات المجاورة كحزمة واحدة
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import create_app

app = create_app()

if __name__ == "__main__":
    # الحصول على البورت من Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
