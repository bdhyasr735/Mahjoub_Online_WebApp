import os
from apps import create_app

app = create_app()

if __name__ == "__main__":
    # Render يضع رقم المنفذ في متغير بيئي
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
