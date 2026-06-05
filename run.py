# 📂 run.py - نسخة آمنة للإنتاج
import os
from apps import create_app
from apps.extensions import db
from apps.models.admin_db import AdminUser

app = create_app()

def initialize_database():
    """
    عملية آمنة: تُنشئ الجداول فقط إذا لم تكن موجودة، 
    ولا تقوم بحذف البيانات الحالية أبداً.
    """
    with app.app_context():
        try:
            db.create_all()  # تنشئ الجداول إذا لم تكن موجودة
            
            # زرع المستخدم "محجوب" فقط إذا كان الجدول فارغاً
            u, p = "محجوب", "123"
            if not AdminUser.query.filter_by(username=u).first():
                new_admin = AdminUser(username=u, phone_number="0000000000", role='Owner')
                new_admin.set_password(p)
                db.session.add(new_admin)
                db.session.commit()
                print("✅ تم التأكد من وجود الهوية السيادية.")
                
        except Exception as e:
            print(f"🚨 خطأ أثناء تهيئة قاعدة البيانات: {e}")

# استدعاء دالة التهيئة
initialize_database()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
