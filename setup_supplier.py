import os
from core import app, db
from core.models.user import User

def setup_system_accounts():
    """
    هذا السكريبت يقوم بتعميد الحسابات السيادية في المنصة اللامركزية
    لضمان التعرف عليها عند تسجيل الدخول.
    """
    with app.app_context():
        # 1. إعداد حساب المورد (محجوب أونلاين)
        supplier_name = "محجوب أونلاين"
        supplier_user = User.query.filter_by(username=supplier_name).first()
        
        if not supplier_user:
            print(f"🚀 جاري إنشاء حساب المورد: {supplier_name}...")
            new_supplier = User(
                username=supplier_name,
                role="supplier",
                status="approved" # معتمد تلقائياً للدخول للداشبورد
            )
            new_supplier.set_password("123")
            db.session.add(new_supplier)
            print(f"✅ تم تسجيل {supplier_name} بنجاح.")
        else:
            # تحديث البيانات للتأكد من مطابقتها للمطلوب
            supplier_user.role = "supplier"
            supplier_user.status = "approved"
            supplier_user.set_password("123")
            print(f"⚠️ حساب {supplier_name} موجود مسبقاً، تم تحديث الصلاحيات وكلمة المرور.")

        # 2. إعداد حساب الإدارة (علي محجوب) لضمان عدم حدوث خطأ "غير مسجل" هناك أيضاً
        admin_name = "علي محجوب"
        admin_user = User.query.filter_by(username=admin_name).first()
        
        if not admin_user:
            print(f"🏛️ جاري إنشاء حساب الإدارة: {admin_name}...")
            new_admin = User(
                username=admin_name,
                role="admin",
                status="approved"
            )
            new_admin.set_password("123")
            db.session.add(new_admin)
            print(f"✅ تم تسجيل القائد {admin_name} بنجاح.")
        else:
            admin_user.role = "admin"
            admin_user.set_password("123")
            print(f"⚠️ حساب {admin_name} موجود مسبقاً، تم تحديث بيانات الإدارة.")

        # حفظ التغييرات نهائياً في قاعدة البيانات
        try:
            db.session.commit()
            print("\n✨ اكتملت العملية! المنصة اللامركزية جاهزة لاستقبالك الآن.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ حدث خطأ أثناء الحفظ: {e}")

if __name__ == "__main__":
    setup_system_accounts()
