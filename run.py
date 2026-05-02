# run.py
# المحرك التشغيلي لمنصة محجوب أونلاين - إصدار الحسم السيادي
import os
from core import create_app, db
from core.models.user import User

# بناء التطبيق بناءً على الإعدادات المركزية
app = create_app()

def initialize_sovereign_system():
    """وظيفة تهيئة الترسانة وتصفير البيانات لمرة واحدة"""
    with app.app_context():
        try:
            print("⏳ جاري تهيئة الترسانة الرقمية وتصفير البيانات القديمة...")
            
            # 1. تصفير شامل للجداول لضمان مطابقة الهيكلية الجديدة (role, is_active_account)
            # drop_all تضمن مسح الجداول القديمة التي تفتقد للأعمدة الجديدة
            db.drop_all() 
            db.create_all()
            
            # 2. إعداد بيانات القائد (علي محجوب)
            target_username = "علي محجوب"
            
            # إنشاء الكائن (Object) الخاص بالمستخدم بالهيكل المعتمد
            admin = User(
                username=target_username,
                role='admin',
                is_active_account=True
            )
            
            # تثبيت كلمة المرور المشفرة (123)
            admin.set_password('123')
            
            # 3. الزرع القسري في قاعدة البيانات
            db.session.add(admin)
            db.session.commit() # الحفظ النهائي والدائم
            
            print(f"✅ تم بنجاح زرع حساب القائد: {admin.username}")
            print(f"🔑 المعرف الرقمي (ID): {admin.id}")
            print(f"🛡️ الحالة: نشط | الرتبة: {admin.role}")
            print("🚀 منصة محجوب أونلاين جاهزة الآن لاستقبال القائد.")

        except Exception as e:
            # في حال حدوث أي خطأ، يتم التراجع لضمان سلامة القاعدة
            db.session.rollback()
            print(f"⚠️ فشل حرج في تهيئة البيانات السيادية: {e}")
            raise e

if __name__ == "__main__":
    # تشغيل عملية التهيئة قبل إقلاع السيرفر
    # ملاحظة: في بيئة الإنتاج الفعلية، يفضل تشغيل هذه الخطوة يدوياً لمرة واحدة
    initialize_sovereign_system()

    # تشغيل السيرفر على المنفذ المخصص لـ Railway
    # استخدام host='0.0.0.0' ضروري للوصول الخارجي عبر الحاوية
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
