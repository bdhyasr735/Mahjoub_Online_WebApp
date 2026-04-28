from core import app, db
from core.models.user import User

def create_supplier():
    with app.app_context():
        # التأكد من عدم تكرار الحساب
        user = User.query.filter_by(username="محجوب أونلاين").first()
        
        if not user:
            # إنشاء الحساب في السجلات اللامركزية
            new_supplier = User(
                username="محجوب أونلاين",
                role="supplier",
                status="approved"
            )
            new_supplier.set_password("123")
            db.session.add(new_supplier)
            db.session.commit()
            print("✅ تم تعميد 'محجوب أونلاين' في قاعدة البيانات.")
        else:
            print("⚠️ الحساب موجود بالفعل في السجلات.")

if __name__ == "__main__":
    create_supplier()
