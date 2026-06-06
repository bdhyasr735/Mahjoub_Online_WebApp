# 📂 seed_db.py
from apps import create_app
from apps.extensions import db
from apps.models.supplier_db import Supplier # تأكد من المسار الصحيح
from apps.models.admin_db import AdminUser

app = create_app()

def seed_data():
    with app.app_context():
        # زراعة الموردين
        if not Supplier.query.first():
            s1 = Supplier(name="مورد تجريبي 1", phone="0123456789")
            db.session.add(s1)
            db.session.commit()
            print("✅ تم زرع الموردين.")

if __name__ == "__main__":
    seed_data()
