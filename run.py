import os
from sqlalchemy import text
from core import create_app, db
from core.models.user import User

app = create_app()

def reset_and_build_database():
    """مسح الجداول القديمة وبناء الهيكل الجديد لضمان وجود كافة الأعمدة"""
    with app.app_context():
        try:
            print("🚨 جاري إعادة تهيئة الهيكل البرمجي للقاعدة...")
            
            # تنفيذ مسح شامل لجدول المستخدم القديم لضمان تحديث الأعمدة
            db.session.execute(text('DROP TABLE IF EXISTS "user" CASCADE;'))
            db.session.commit()
            print("🗑️ تم مسح الجداول القديمة بنجاح.")
            
            # بناء الجداول من جديد بالأعمدة (is_active_account و role)
            db.create_all()
            print("🏗️ تم بناء الترسانة الرقمية بالهيكل الجديد.")

            # تنصيب القائد "علي محجوب"
            admin_username = "علي محجوب"
            new_admin = User(username=admin_username, role='admin')
            new_admin.set_password('123')
            db.session.add(new_admin)
            db.session.commit()
            print(f"👑 تم تنصيب القائد {admin_username} بنجاح.")

        except Exception as e:
            db.session.rollback()
            print(f"❌ تعثرت العملية بسبب: {str(e)}")

# تشغيل عملية الإصلاح لمرة واحدة عند بدء الحاوية
reset_and_build_database()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
