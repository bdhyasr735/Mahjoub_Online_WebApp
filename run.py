# 📂 run.py - مع تحديث تلقائي للجداول
import os
from apps import create_app
from apps.extensions import db
from apps.models.admin_db import AdminUser

def setup_sovereign_identity():
    with app.app_context():
        try:
            # 1. تحديث هيكل الجداول لإضافة الأعمدة الناقصة تلقائياً
            db.create_all() 
            
            # 2. الآن نقوم بالحقن
            u, p = "محجوب", "123"
            existing = AdminUser.query.filter_by(username=u).first()
            if not existing:
                new_admin = AdminUser(username=u, phone_number="0000000000", role='Owner')
                new_admin.set_password(p)
                db.session.add(new_admin)
                db.session.commit()
                print(f"✅ تم زرع الهوية السيادية بنجاح: {u}")
            else:
                print(f"ℹ️ الهوية {u} موجودة مسبقاً.")
        except Exception as e:
            print(f"⚠️ فشل الحقن: {e}")

app = create_app()
setup_sovereign_identity()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
