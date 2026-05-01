# run.py
# الملف الرئيسي لتشغيل محرك منصة محجوب أونلاين السيادي
from core import create_app, db
from core.models.user import User

# بناء التطبيق
app = create_app()

if __name__ == "__main__":
    with app.app_context():
        try:
            # 1. إنشاء الجداول إذا لم تكن موجودة
            db.create_all()
            
            # 2. تثبيت بيانات الإدارة (علي محجوب)
            # نبحث عن الحساب للتأكد من عدم التكرار
            admin = User.query.filter_by(username='علي محجوب').first()
            
            if admin:
                # تحديث البيانات الحالية لضمان مطابقتها لطلبك
                admin.role = 'admin'
                admin.set_password('123') # سيتم تشفيرها لـ Hash تلقائياً
                admin.is_active_account = True
                print("🔄 تم تحديث بيانات القائد (علي محجوب) بنجاح.")
            else:
                # إنشاء الحساب لأول مرة إذا لم يكن موجوداً
                new_admin = User(
                    username='علي محجوب',
                    role='admin',
                    is_active_account=True,
                    email='ali@mahjoub.online'
                )
                new_admin.set_password('123')
                db.session.add(new_admin)
                print("🚀 تم تسجيل القائد (علي محجوب) في القاعدة الدائمة.")
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ فشل في تثبيت بيانات الإدارة: {e}")

    # تشغيل السيرفر
    app.run(host='0.0.0.0', port=8080)
