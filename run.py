import os
from sqlalchemy import text
from core import create_app, db
from core.models.user import User

# 1. إنشاء التطبيق
app = create_app()

def initialize_system():
    """تهيئة النظام السيادي وقاعدة البيانات عند الإقلاع"""
    with app.app_context():
        try:
            # التأكد من وجود الجداول (بدون مسح البيانات لضمان الاستقرار)
            db.create_all()
            
            # التأكد من وجود الحساب الإداري للقائد علي محجوب
            admin_username = "علي محجوب"
            admin = User.query.filter_by(username=admin_username).first()
            if not admin:
                new_admin = User(username=admin_username, role='admin')
                new_admin.set_password('123')
                db.session.add(new_admin)
                db.session.commit()
                print("✅ تم تأكيد صلاحيات القائد في النظام.")
        except Exception as e:
            print(f"⚠️ تنبيه النظام: {str(e)}")

# تنفيذ التهيئة قبل بدء استقبال الطلبات
initialize_system()

if __name__ == "__main__":
    # Railway يتطلب الربط مع المنفذ الديناميكي PORT
    # إذا لم يجد PORT، سيستخدم 5000 كافتراضي
    port = int(os.environ.get("PORT", 5000))
    
    # host='0.0.0.0' ضروري جداً لجعل السيرفر مرئياً للخارج
    app.run(host='0.0.0.0', port=port, debug=False)
