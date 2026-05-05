import os
from core import create_app, db
from sqlalchemy import text

app = create_app()

def initialize_database():
    with app.app_context():
        try:
            print("--------------------------------")
            print("🚀 جاري تنفيذ بروتوكول الإصلاح الشامل لـ محجوب أونلاين...")
            
            # 1. ضمان وجود الجداول الأساسية
            from core.models.user import User
            try:
                from core.models.business import Order
                from core.models.product import Product
            except ImportError:
                print("⚠️ تنبيه: تعذر استيراد بعض الموديلات.")
            
            db.create_all()
            
            # 2. الترميم الهيكلي العميق (Deep Structural Repair)
            with db.engine.connect() as connection:
                print("🔍 فحص وترميم أعمدة جدول الطلبات (Orders)...")
                
                # إضافة كافة الأعمدة المفقودة التي ظهرت في سجلات Railway
                connection.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id);"))
                connection.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS total_amount FLOAT DEFAULT 0.0;"))
                connection.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'YER';"))
                connection.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'pending';"))
                connection.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS shipping_address TEXT;"))
                connection.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS contact_phone VARCHAR(20);"))
                
                # إضافة أعمدة جدول المنتجات لضمان جاهزية العرض
                print("🔍 فحص وترميم أعمدة جدول المنتجات (Products)...")
                connection.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS owner_id INTEGER REFERENCES users(id);"))
                connection.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'YER';"))
                connection.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS stock_quantity INTEGER DEFAULT 0;"))
                
                # إضافة عمود الصلاحيات للمستخدمين (لحل مشكلة الداشبورد)
                connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'admin';"))
                
                connection.commit()
            
            print("✅ اكتمل الترميم! كافة الأعمدة (Shipping, Phone, UserID) أصبحت جاهزة.")
            print("🌟 محجوب أونلاين جاهز الآن للانطلاق.")
            print("--------------------------------")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ تعثرت عملية الترميم: {str(e)}")

if __name__ == "__main__":
    initialize_database()
