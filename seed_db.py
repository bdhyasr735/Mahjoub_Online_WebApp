# 📂 seed_db.py
from apps import create_app
from apps.extensions import db
from apps.models.admin_db import AdminUser
from apps.models.supplier_db import Supplier
from werkzeug.security import generate_password_hash

app = create_app()

def seed_system():
    with app.app_context():
        # --- 1. زرع "محجوب" ---
        admin = AdminUser.query.filter_by(username="محجوب").first()
        if not admin:
            admin = AdminUser(username="محجوب", phone_number="0000000000", role='Owner')
            admin.set_password("123")
            db.session.add(admin)
            print("✅ تم إنشاء الهوية السيادية: محجوب")
        
        # --- 2. زرع الموردين ---
        # لاحظ أننا نستخدم الـ Properties (مثل trade_name) ليقوم الموديل بالتشفير تلقائياً
        suppliers_data = [
            {
                "username": "supplier_1", 
                "trade_name": "مؤسسة التوريد الأولى", 
                "owner_phone": "0500000001",
                "password_hash": generate_password_hash("123456")
            }
        ]

        for data in suppliers_data:
            if not Supplier.query.filter_by(username=data["username"]).first():
                new_s = Supplier(
                    username=data["username"],
                    password_hash=data["password_hash"],
                    trade_name=data["trade_name"], # سيتم تشفيرها تلقائياً عبر @trade_name.setter
                    owner_phone=data["owner_phone"] # سيتم تشفيرها تلقائياً عبر @owner_phone.setter
                )
                db.session.add(new_s)
                print(f"✅ تم زرع المورد: {data['trade_name']}")

        db.session.commit()
        print("🚀 اكتملت عملية الزرع بنجاح.")

if __name__ == "__main__":
    seed_system()
