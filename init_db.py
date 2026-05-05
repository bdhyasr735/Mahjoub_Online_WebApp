import os
from core import create_app, db
from sqlalchemy import text

# إنشاء نسخة من التطبيق للوصول إلى سياق قاعدة البيانات لـ محجوب أونلاين
app = create_app()

def initialize_database():
    with app.app_context():
        try:
            print("--------------------------------")
            print("🚀 جاري الاتصال وبناء الترسانة الرقمية لـ محجوب أونلاين...")
            
            # 1. استيراد الموديلات لضمان تعريف الجداول في SQLAlchemy
            from core.models.user import User
            try:
                from core.models.business import Order
                from core.models.product import Product
            except ImportError:
                print("⚠️ تنبيه: تعذر استيراد بعض موديلات العمليات.")
            
            # 2. إنشاء الجداول الجديدة (التي لم تكن موجودة سابقاً)
            db.create_all()
            
            # 3. الترميم الهيكلي السيادي (حل مشكلة العمود المفقود في image_001738.png)
            with db.engine.connect() as connection:
                print("🔍 بدء عملية الترميم العميق للجداول القائمة...")
                
                # --- إصلاح جدول المستخدمين (Users) ---
                connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'admin';"))
                connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active_account BOOLEAN DEFAULT TRUE;"))
                
                # --- إصلاح جدول الطلبات (Orders) - الحل النهائي للخطأ ---
                print("🛠️ معالجة جدول الطلبات (Orders)...")
                connection.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id);"))
                connection.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS total_amount FLOAT DEFAULT 0.0;"))
                connection.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'YER';"))
                connection.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'pending';"))
                
                # --- إصلاح جدول المنتجات (Products) ---
                print("🛠️ معالجة جدول المنتجات (Products)...")
                connection.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS owner_id INTEGER REFERENCES users(id);"))
                connection.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'YER';"))
                connection.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS stock_quantity INTEGER DEFAULT 0;"))
                
                # تأكيد كافة التغييرات في قاعدة البيانات
                connection.commit()
            
            print("✅ تم فحص وترميم هيكل قاعدة البيانات بنجاح (تمت إضافة الأعمدة المفقودة).")
            print("🌟 الترسانة الرقمية جاهزة الآن للتشغيل في بيئة Railway.")
            print("--------------------------------")
            
        except Exception as e:
            db.session.rollback()
            print("--------------------------------")
            print(f"❌ تعثرت عملية البناء السيادي: {str(e)}")
            print("--------------------------------")

if __name__ == "__main__":
    initialize_database()
