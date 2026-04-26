import os
from core import create_app, db
# استدعاء الموديلات من النواة المركزية الموحدة
from core.models import User, Supplier, Product 

app = create_app()

with app.app_context():
    try:
        print("🔄 [System] جاري تحديث الهيكل السيادي للمجداول...")
        # حذف كل شيء لبناء الأرضية من جديد
        db.drop_all() 
        db.create_all() 
        
        # إنشاء حساب "القائد العام"
        admin = User(
            username='علي محجوب', 
            password='123', # تذكر تغييرها لاحقاً يا عظيم
            role='admin'
        )
        
        # إنشاء مورد تجريبي لاختبار نظام المحافظ
        supplier = Supplier(
            name='مورد تجريبي', 
            password='123', 
            email='test@mahjoub.online',
            is_approved=True,
            province='الحديدة', #
            wallet_sar=0.00,
            wallet_usd=0.00
        )
        
        db.session.add(admin)
        db.session.add(supplier)
        db.session.commit()
        print("✅ [Database] تم تحديث الهيكل بالكامل بنجاح. 'description' الآن نشط!")

    except Exception as e:
        db.session.rollback()
        print(f"⚠️ [Error] فشل التحديث: {e}")

if __name__ == "__main__":
    # التوافق مع Railway و Render
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
