import os
from sqlalchemy import text
from core import create_app, db
from core.models.user import User

# 1. إنشاء التطبيق
app = create_app()

def patch_database():
    """فحص وإصلاح هيكل الجداول (الترسانة) تلقائياً"""
    with app.app_context():
        # قائمة بالأعمدة الجديدة التي نحتاج للتأكد من وجودها
        sql_commands = [
            # إضافة العمود الذي تسبب في التعثر وربطه بالمستخدمين
            "ALTER TABLE vendors ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id);",
            
            # إضافة حقول الهوية والأرشفة والموقع والربط المالي
            "ALTER TABLE vendors ADD COLUMN IF NOT EXISTS id_type VARCHAR(100);",
            "ALTER TABLE vendors ADD COLUMN IF NOT EXISTS id_card_number VARCHAR(100);",
            "ALTER TABLE vendors ADD COLUMN IF NOT EXISTS id_image VARCHAR(255);",
            "ALTER TABLE vendors ADD COLUMN IF NOT EXISTS activity_type VARCHAR(100);",
            "ALTER TABLE vendors ADD COLUMN IF NOT EXISTS province VARCHAR(100);",
            "ALTER TABLE vendors ADD COLUMN IF NOT EXISTS district VARCHAR(100);",
            "ALTER TABLE vendors ADD COLUMN IF NOT EXISTS address_detail VARCHAR(255);",
            "ALTER TABLE vendors ADD COLUMN IF NOT EXISTS bank_name VARCHAR(150);",
            "ALTER TABLE vendors ADD COLUMN IF NOT EXISTS bank_acc VARCHAR(100);",
            "ALTER TABLE vendors ADD COLUMN IF NOT EXISTS fin_type VARCHAR(50);"
        ]
        
        for cmd in sql_commands:
            try:
                db.session.execute(text(cmd))
                db.session.commit()
            except Exception:
                db.session.rollback()
                # نتجاهل الأخطاء هنا لأن العمود قد يكون موجوداً بالفعل
                continue

def initialize_system():
    """تهيئة النظام السيادي وقاعدة البيانات عند الإقلاع"""
    with app.app_context():
        try:
            # 1. تحديث هيكل الجداول أولاً لإصلاح أي نقص
            patch_database()
            
            # 2. التأكد من وجود الجداول الأساسية
            db.create_all()
            
            # 3. التأكد من وجود الحساب الإداري للقائد علي محجوب
            admin_username = "علي محجوب"
            admin = User.query.filter_by(username=admin_username).first()
            if not admin:
                new_admin = User(username=admin_username, role='admin')
                new_admin.set_password('123')
                db.session.add(new_admin)
                db.session.commit()
                print("✅ تم تأكيد صلاحيات القائد وتحديث الترسانة في النظام.")
            else:
                print("✅ النظام والترسانة في حالة جاهزية تامة.")
        except Exception as e:
            print(f"⚠️ تنبيه النظام: {str(e)}")

# تنفيذ التهيئة والإصلاح قبل بدء استقبال الطلبات
initialize_system()

if __name__ == "__main__":
    # Railway يتطلب الربط مع المنفذ الديناميكي PORT
    port = int(os.environ.get("PORT", 5000))
    
    # تشغيل التطبيق (نضع debug=False في الإنتاج على Railway)
    app.run(host='0.0.0.0', port=port, debug=False)
