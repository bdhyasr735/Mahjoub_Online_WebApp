# coding: utf-8
# 📂 run.py - وضع التطهير وإعادة البناء الذكي

import os
from apps import create_app
from apps.extensions import db
from apps.models.admin_db import AdminUser

# 1. تهيئة التطبيق
app = create_app()

def reset_and_seed():
    """
    عملية التطهير وإعادة البناء:
    تستخدم لمرة واحدة فقط لمزامنة هيكل قاعدة البيانات بعد إضافة الأعمدة المشفرة.
    """
    with app.app_context():
        try:
            print("⚠️ بدء عملية تطهير وإعادة بناء الجداول...")
            
            # حذف جميع الجداول الحالية لضمان مطابقة الهيكل الجديد
            db.drop_all() 
            print("🗑️ تم حذف الجداول القديمة.")
            
            # إنشاء الجداول من جديد وفق الكود الحالي
            db.create_all()
            print("🏗️ تم إنشاء الجداول الجديدة بنجاح.")
            
            # زرع المستخدم "محجوب" كـ Owner (هوية سيادية)
            u, p = "محجوب", "123"
            if not AdminUser.query.filter_by(username=u).first():
                new_admin = AdminUser(username=u, phone_number="0000000000", role='Owner')
                new_admin.set_password(p)
                db.session.add(new_admin)
                db.session.commit()
                print(f"✅ تم زرع الهوية السيادية بنجاح: {u}")
            
        except Exception as e:
            print(f"🚨 خطأ فادح أثناء إعادة البناء: {e}")

# تنفيذ العملية فور التشغيل
reset_and_seed()

if __name__ == "__main__":
    # استخدام المنفذ المخصص من Render أو 10000 كافتراضي
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
