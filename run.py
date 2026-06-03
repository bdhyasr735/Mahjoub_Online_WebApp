# coding: utf-8
import os
from apps import create_app

# هذا المتغير هو ما يبحث عنه Gunicorn (يجب أن يكون في المستوى العلوي للملف)
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
