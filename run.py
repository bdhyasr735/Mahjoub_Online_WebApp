# run.py
# coding: utf-8
# 🚀 المحرك التنفيذي لمنصة محجوب أونلاين 2026
# التوثيق: تشغيل السيرفر وتعميد صلاحيات المالك السيادي وتحديث هيكل البيانات تلقائياً

import os
from apps import create_app, db
from werkzeug.security import generate_password_hash
from sqlalchemy import text # استيراد أداة تنفيذ النصوص البرمجية المباشرة

# 1. إنشاء نسخة التطبيق عبر المصنع المركزي
app = create_app()

def initialize_sovereignty():
    """
    دالة تعميد السيادة: لضمان تصفير الجداول القديمة والمتعارضة،
    وإعادة بناء الهيكلية الموحدة للمحافظ، وتعميد حساب المالك (علي محجوب) في Railway.
    """
    with app.app_context():
        try:
            # 🚨 [خطوة الحوكمة الأولى والطارئة]: كسر القيود وتطهير الجداول المتعارضة
            print("⏳ جاري تنظيف الجداول القديمة وكسر قيود التحقق بالتتابع عبر CASCADE...")
            
            # تنفيذ أوامر الحذف الصارمة لضمان إخلاء مساحة البنية الجديدة
            db.session.execute(text("DROP TABLE IF EXISTS wallet_transactions CASCADE;"))
            db.session.execute(text("DROP TABLE IF EXISTS supplier_wallets CASCADE;"))
            db.session.execute(text("DROP TABLE IF EXISTS wallets CASCADE;"))
            db.session.execute(text("DROP TABLE IF EXISTS suppliers CASCADE;"))
            db.session.commit()
            
            print("✨ تم مسح الجداول القديمة بنجاح، جاري بناء الهيكلية الموحدة الجديدة...")

            # 🚨 استدعاء محلي متأخر للموديل هنا لحماية خط الإقلاع ومنع الـ Circular Import تماماً
            from apps.models.admin_db import AdminUser
            from apps.models.supplier_db import Supplier
            from apps.models.wallet_db import Wallet

            # [التحديث الجوهري الثاني]: إنشاء الجداول الجديدة بالهوية والمحفظة المشتقة تلقائياً
            print("⏳ جاري مواءمة وتحديث هيكل السجلات السيادية وقاعدة البيانات...")
            db.create_all()
            
            # [التحديث الجوهري الثالث]: ترقيع جدول الموردين (Suppliers) بالأعمدة الناقصة تلقائياً في PostgreSQL
            print("🛡️ جاري التحقق من الأعمدة الحوكمة لجدول الموردين...")
            alter_query = """
            ALTER TABLE suppliers 
            ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active',
            ADD COLUMN IF NOT EXISTS rank_grade VARCHAR(50),
            ADD COLUMN IF NOT EXISTS registration_source VARCHAR(100) DEFAULT 'لوحة التحكم',
            ADD COLUMN IF NOT EXISTS created_by_id INTEGER,
            ADD COLUMN IF NOT EXISTS updated_by_id INTEGER,
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            """
            # تنفيذ الاستعلام المباشر لترقيع الجدول دون المساس بالبيانات القديمة
            db.session.execute(text(alter_query))
            db.session.commit()
            print("🚀 تم تحديث جداول وأعمدة قاعدة البيانات بنجاح تام.")
            
            # البحث عن حساب المؤسس في قاعدة البيانات
            owner = AdminUser.query.filter_by(username='علي محجوب').first()
            
            if not owner:
                print("🛡️ جاري إنشاء حساب المالك السيادي للمنصة...")
                new_owner = AdminUser(
                    username='علي محجوب',
                    password_hash=generate_password_hash('123'),
                    role='Owner' # المالك والسيادة المطلقة
                )
                db.session.add(new_owner)
                db.session.commit()
                print("✅ تم تعميد 'علي محجوب' مالكاً رسمياً لنظام حوكمة التجارة الرقمية.")
            else:
                print(f"📡 نظام الحوكمة مستقر: المالك '{owner.username}' متصل وقيد العمل.")
                
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ تنبيه تقني: تعذر تحديث قاعدة البيانات أو الوصول للجداول أثناء البدء: {e}")

if __name__ == "__main__":
    # تنفيذ إجراءات التأكد من الحسابات وتحديث هيكل البيانات قبل إقلاع السيرفر
    initialize_sovereignty()
    
    # تحديد المنفذ (Port) ليتوافق مع بيئة Railway السحابية
    port = int(os.environ.get("PORT", 5000))
    
    # تشغيل المحرك
    # في بيئة الإنتاج على Railway، يفضل جعل debug=False لرفع أداء السيرفر وحمايته
    app.run(host='0.0.0.0', port=port, debug=False)
