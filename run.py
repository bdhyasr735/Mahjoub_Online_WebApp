from core import create_app

# إنشاء نسخة التطبيق من المحرك المركزي
app = create_app()

if __name__ == '__main__':
    # تشغيل السيرفر المحلي على المنفذ 5000
    # ملاحظة: سيقوم التطبيق تلقائياً بالاتصال بقاعدة Render السحابية
    app.run(debug=True, port=8080)
