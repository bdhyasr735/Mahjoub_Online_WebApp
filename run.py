import os
from core import create_app, db

# 1. إنشاء نسخة التطبيق عبر دالة المصنع
app = create_app()

# 2. إدارة قاعدة البيانات وإنشاء الحساب السيادي
with app.app_context():
    try:
        # إنشاء الجداول إذا لم تكن موجودة
        db.create_all()
        print("✅ [Database] تم مزامنة الجداول مع قاعدة البيانات بنجاح.")

        # استيراد مودل المستخدم لإنشاء حساب القائد
        from core.models import User
        
        # التحقق من وجود حساب "علي محجوب" لعدم التكرار
        admin_name = 'علي محجوب'
        if not User.query.filter_by(username=admin_name).first():
            # إنشاء الحساب الأول (القائد)
            # ملاحظة: كلمة المرور هنا '123' يمكنك تغييرها لاحقاً من لوحة التحكم
            new_admin = User(username=admin_name, password='123', role='admin')
            db.session.add(new_admin)
            db.session.commit()
            print(f"👤 [Security] تم إنشاء حساب القائد '{admin_name}' بنجاح. يمكنك الدخول الآن.")
        else:
            print(f"ℹ️ [Security] حساب القائد '{admin_name}' موجود مسبقاً وجاهز للعمل.")

    except Exception as e:
        print(f"⚠️ [Database/Security] تنبيه أثناء الإقلاع: {e}")

if __name__ == "__main__":
    # 3. جلب المنفذ (Port) من Railway/Render
    port = int(os.environ.get("PORT", 8080))
    
    # 4. تشغيل السيرفر (تعطيل الـ Debug لضمان استقرار جلسات الدخول)
    print(f"🚀 Mahjoub Online is launching on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
