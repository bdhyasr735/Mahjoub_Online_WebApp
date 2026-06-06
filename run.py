# 📂 run.py - النسخة المحصنة تماماً
import os
from apps import create_app
from apps.extensions import db
from apps.models.admin_db import AdminUser

# 1. تهيئة التطبيق (هذا لا يحتاج قاعدة بيانات)
app = create_app()

def initialize_system():
    """هذه الدالة تحاول تشغيل المهام فقط إذا كان التطبيق مستعداً."""
    try:
        with app.app_context():
            # بناء الجداول
            db.create_all()
            
            # التأكد من هوية "محجوب"
            admin = AdminUser.query.filter_by(username="محجوب").first()
            if not admin:
                new_admin = AdminUser(username="محجوب", phone_number="0000000000", role='Owner')
                new_admin.set_password("123")
                db.session.add(new_admin)
                db.session.commit()
                print("✅ نظام محجوب: تم إنشاء الهوية السيادية.")
    except Exception as e:
        # هنا السر: بدلاً من إظهار "خطأ أحمر" يوقف السيرفر، سنقوم بطباعة رسالة فقط
        print(f"⚠️ تنبيه نظام محجوب: لم نتمكن من زرع البيانات حالياً (ربما القاعدة لم تجهز بعد): {e}")

if __name__ == "__main__":
    # تشغيل المهام
    initialize_system()
    
    # تشغيل السيرفر
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
