# 📂 run.py - وضع التطهير وإعادة البناء
import os
from apps import create_app
from apps.extensions import db
from apps.models.admin_db import AdminUser

def reset_and_seed():
    with app.app_context():
        try:
            print("⚠️ بدء عملية تطهير وإعادة بناء الجداول...")
            
            # 1. حذف جميع الجداول الحالية (تطهير كامل)
            db.drop_all() 
            print("🗑️ تم حذف الجداول القديمة.")
            
            # 2. إنشاء الجداول من جديد وفق الكود الحالي
            db.create_all()
            print("🏗️ تم إنشاء الجداول الجديدة.")
            
            # 3. زرع المستخدم "محجوب"
            u, p = "محجوب", "123"
            new_admin = AdminUser(username=u, phone_number="0000000000", role='Owner')
            new_admin.set_password(p)
            db.session.add(new_admin)
            db.session.commit()
            print(f"✅ تم زرع الهوية السيادية بنجاح: {u}")
            
        except Exception as e:
            print(f"🚨 خطأ فادح أثناء إعادة البناء: {e}")

app = create_app()
reset_and_seed() # تشغيل عملية التطهير مرة واحدة فقط

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
