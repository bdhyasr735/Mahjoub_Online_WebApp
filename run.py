import os
from sqlalchemy import text
from core import create_app, db
from core.models.user import User

app = create_app()

def boot_system():
    with app.app_context():
        try:
            # تصفير قسري لضمان تحديث الأعمدة الجديدة
            db.session.execute(text('DROP TABLE IF EXISTS "user" CASCADE;'))
            db.create_all()
            
            # زرع حساب القائد علي محجوب
            admin = User(username="علي محجوب", role='admin', is_active_account=True)
            admin.set_password('123')
            db.session.add(admin)
            db.session.commit()
            print("🚀 النظام جاهز: المستخدم (علي محجوب) / كلمة المرور (123)")
        except Exception as e:
            print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    boot_system()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
