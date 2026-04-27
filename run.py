import os
import sys

# إجبار بايثون على إضافة المسار الحالي للمشروع
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import create_app

app = create_app()

if __name__ == "__main__":
    # التوافق مع بورت Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
