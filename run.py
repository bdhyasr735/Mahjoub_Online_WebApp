import os
from core import create_app

app = create_app()

if __name__ == "__main__":
    # الحصول على البورت من Railway أو استخدام 5000 كافتراضي
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
