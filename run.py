# run.py
# الملف الرئيسي لتشغيل محرك منصة محجوب أونلاين السيادي
from core import create_app, db
from core.models.user import User # استيراد الموديل لإنشاء الحساب الأول

# بناء التطبيق باستخدام المصنع (Factory Pattern)
app = create_app()

if __name__ == "__main__":
    with app.app_context():
        # 1. التأكد من إنشاء جميع الجداول (الترسانة الرقمية)
        try:
            db.create_all()
            print("✅ تم فحص وإنشاء جداول قاعدة البيانات بنجاح.")
            
            # 2. إنشاء حساب القائد (علي محجوب) تلقائياً إذا لم يكن موجوداً
            admin_user = User.query.filter_by(username='علي').first()
            if not admin_user:
                print("🚀 جاري إنشاء حساب القائد الأول...")
                new_admin = User(
                    username='علي',
                    email='admin@mahjoub.online',
                    role='admin', # منح صلاحيات المدير كاملة
                    is_active_account=True
                )
                # تعيين كلمة مرور افتراضية (تأكد من تغييرها لاحقاً للأمان)
                new_admin.set_password('123456') 
                
                db.session.add(new_admin)
                db.session.commit()
                print("✨ تم إنشاء حساب القائد بنجاح [المستخدم: علي | السر: 123456]")
            else:
                print("ℹ️ حساب القائد (علي) موجود مسبقاً وجاهز للعمل.")
                
        except Exception as e:
            print(f"⚠️ فشل في تهيئة قاعدة البيانات أو الحسابات: {e}")
            db.session.rollback()

    # تشغيل السيرفر؛ تم ضبط المنفذ 8080 ليتوافق مع إعدادات Railway
    # ملاحظة: Gunicorn في Railway سيتجاهل هذا السطر ويستخدم المنفذ تلقائياً
    app.run(host='0.0.0.0', port=8080)
