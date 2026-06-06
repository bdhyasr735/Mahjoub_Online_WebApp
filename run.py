# coding: utf-8
# 📂 run.py (موجود في المجلد الرئيسي بجانب config.py)

from apps import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
