# 📂 run.py - نسخة الإنتاج ذاتية الإصلاح (Self-Healing)
import os
from apps import create_app
from apps.extensions import db
from apps.models.admin_db import AdminUser
from sqlalchemy import text

app = create_app()

def auto_repair_db():
    """
    يقوم هذا النظام بالتأكد من وجود أعمدة البحث 
    وإضافتها تلقائياً إذا كانت مفقودة عند كل تشغيل.
    """
    with app.app_context():
        try:
            # 1. إنشاء الجداول إذا كانت غير موجودة
            db.create_all()
            
            # 2. فحص وإصلاح الأعمدة (إضافة أعمدة البحث إذا لم تكن موجودة)
            db.session.execute(text("ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS search_name VARCHAR(150);"))
            db.session.execute(text("ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS search_phone VARCHAR(20);"))
            db.session.commit()
            print("✅ نظام الإصلاح الذاتي: قاعدة البيانات محدثة وجاهزة.")
            
            # 3. زرع الهوية السيادية
            u, p = "محجوب", "123"
            if not AdminUser.query.filter_by(username=u).first():
                new_admin = AdminUser(username=u, phone_number="0000000000", role='Owner')
                new_admin.set_password(p)
                db.session.add(new_admin)
                db.session.commit()
                print("✅ تم التأكد من وجود الهوية السيادية.")
                
        except Exception as e:
            print(f"🚨 خطأ في نظام الإصلاح التلقائي: {e}")
            db.session.rollback()

# تشغيل عملية الإصلاح قبل بداية السيرفر
auto_repair_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
