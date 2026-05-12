import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# تعريف محلي لضمان التشغيل المستقل
db = SQLAlchemy()

def sovereign_reset():
    print("🧹 بدء بروتوكول التطهير الشامل...")
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        try:
            # استيراد الموديل الجديد لتعميده
            from core.models.supplier_db import Supplier
            
            print("⚠️ جاري مسح الجداول القديمة (Drop All)...")
            db.drop_all() 
            
            print("💎 جاري بناء الهيكل السيادي الجديد (Create All)...")
            db.create_all()
            
            print("✅ تم التطهير وبناء الجداول بنجاح.")
        except Exception as e:
            print(f"❌ خطأ أثناء التأسيس: {e}")

if __name__ == "__main__":
    sovereign_reset()
