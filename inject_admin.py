# 📂 inject_admin.py
# تم تعديل الكود لدعم الاسم باللغة العربية والزراعة المباشرة
from apps import create_app
from apps.extensions import db
from apps.models.admin_db import AdminUser

def inject_sovereign_admin(username, password, phone):
    app = create_app()
    with app.app_context():
        # التحقق من وجود المستخدم (الاسم باللغة العربية: محجوب)
        existing = AdminUser.query.filter_by(username=username).first()
        if existing:
            print(f"⚠️ المستخدم {username} موجود مسبقاً في قاعدة البيانات.")
            return

        # إنشاء المستخدم الجديد باسم "محجوب"
        new_admin = AdminUser(
            username=username,
            phone_number=phone,
            role='Owner' 
        )
        new_admin.set_password(password)
        
        db.session.add(new_admin)
        db.session.commit()
        print(f"✅ تم حقن الهوية السيادية بنجاح للمستخدم: {username}")

if __name__ == "__main__":
    # الزراعة المباشرة باسم "محجوب" وكلمة مرور "123"
    inject_sovereign_admin("محجوب", "123", "0000000000")
