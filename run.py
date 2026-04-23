import os
from core import create_app, db

# إنشاء التطبيق
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        try:
            # اختبار الاتصال برابط Render الذي وضعته في Variables
            db.engine.connect()
            print("--- ✅ Connection to Render Success! ---")
        except Exception as e:
            print(f"--- ❌ Connection Failed: {str(e)} ---")

    # تحديد المنفذ تلقائياً لـ Railway
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
