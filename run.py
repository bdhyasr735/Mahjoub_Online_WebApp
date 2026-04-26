# run.py المعدل للإصلاح
import os
from core import create_app, db

app = create_app()

with app.app_context():
    try:
        # 🚨 الإجراء الجراحي: تفعيل المسح لإعادة بناء الحقول الجديدة (مثل description)
        print("🔄 [System] جاري تحديث الهيكل السيادي للمجداول...")
        db.drop_all() 
        db.create_all() 
        
        from core.models.user import User
        from core.models.supplier import Supplier
        
        # إعادة إنشاء الحسابات فوراً بعد المسح
        admin = User(username='علي محجوب', password='123', role='admin')
        supplier = Supplier(
            name='مورد تجريبي', 
            password='123', 
            email='test@mahjoub.online',
            is_approved=True,
            province='الحديدة'
        )
        
        db.session.add(admin)
        db.session.add(supplier)
        db.session.commit()
        print("✅ [Database] تم تحديث العمود 'description' وجميع الحقول بنجاح.")

    except Exception as e:
        print(f"⚠️ [Error] فشل التحديث: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
