# run.py
# coding: utf-8
# 🚀 المحرك التنفيذي وفرمان الحوكمة الشاملة لمنصة محجوب أونلاين 2026
# التوثيق: إخضاع قاعدة البيانات وسحق تعارض جداول المحافظ والموردين قسرياً

import os
from apps import create_app, db
from werkzeug.security import generate_password_hash
from sqlalchemy import text # استيراد أداة تنفيذ النصوص البرمجية المباشرة

# 1. إنشاء نسخة التطبيق عبر المصنع المركزي
app = create_app()

def initialize_sovereignty():
    """
    دالة التطهير المطلق: تعطيل القيود الهيكلية مؤقتاً لسحق الجداول القديمة 
    وإعادة ولادة الفضاء الرقمي الموحد دون أي تعليق من PostgreSQL.
    """
    with app.app_context():
        try:
            print("⏳ جاري إخضاع قاعدة البيانات وتعطيل قيود الفحص اللحظي...")
            
            # 🚨 [خطوة الإخضاع الحاسمة]: تأجيل وفصل فحص قيود المفاتيح الأجنبية لمنع اعتراض عملية الـ DROP
            db.session.execute(text("SET CONSTRAINTS ALL DEFERRED;"))
            
            # 🚨 [خطوة التطهير القصوى]: مسح الجداول المتعارضة عبر CASCADE لقطع دابر الامتدادات القديمة وسحق البيانات المخزنة
            print("⏳ جاري سحق الجداول القديمة عبر CASCADE لمنع أخطاء الأرصدة الناقصة...")
            db.session.execute(text("DROP TABLE IF EXISTS wallet_transactions CASCADE;"))
            db.session.execute(text("DROP TABLE IF EXISTS supplier_wallets CASCADE;"))
            db.session.execute(text("DROP TABLE IF EXISTS wallets CASCADE;"))
            db.session.execute(text("DROP TABLE IF EXISTS suppliers CASCADE;"))
            db.session.commit()
            
            print("✨ تم تطهير قاعدة البيانات بالكامل من السجلات المتعارضة والبيانات القديمة.")

            # استدعاء محلي للموديلات لتوثيق الـ Event Listeners والربط الهيكلي الجديد
            from apps.models.admin_db import AdminUser
            from apps.models.supplier_db import Supplier
            from apps.models.wallet_db import Wallet

            # [إعادة البناء الهيكلي]: إنشاء الجداول بالبنية الحوكمية الصافية والجديدة تماماً
            print("⏳ جاري مواءمة وبناء الهيكلية السيادية للمحافظ والموردين...")
            db.create_all()
            
            # [تحديث أعمدة الحوكمة]: إعداد جدول الموردين (Suppliers) الجديد وحقن الحقول اللوجستية
            print("🛡️ جاري مواءمة الأعمدة الحوكمة للجدول السيادي...")
            alter_query = """
            ALTER TABLE suppliers 
            ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active',
            ADD COLUMN IF NOT EXISTS rank_grade VARCHAR(50) DEFAULT 'ريادي',
            ADD COLUMN IF NOT EXISTS registration_source VARCHAR(100) DEFAULT 'لوحة التحكم',
            ADD COLUMN IF NOT EXISTS created_by_id INTEGER,
            ADD COLUMN IF NOT EXISTS updated_by_id INTEGER,
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            """
            db.session.execute(text(alter_query))
            db.session.commit()
            print("🚀 تم بناء البنية وجداول الفضاء المالي بنجاح تام.")
            
            # تأمين حساب المؤسس والمالك السيادي للمنصة
            owner = AdminUser.query.filter_by(username='علي محجوب').first()
            
            if not owner:
                print("🛡️ جاري تعميد حساب المالك السيادي للمنصة...")
                new_owner = AdminUser(
                    username='علي محجوب',
                    password_hash=generate_password_hash('123'),
                    role='Owner'
                )
                db.session.add(new_owner)
                db.session.commit()
                print("✅ تم تعميد 'علي محجوب' مالكاً رسمياً لنظام الحوكمة الرقمية.")
            else:
                print(f"📡 نظام الحوكمة مستقر: المالك '{owner.username}' متصل وقيد العمل.")
                
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ تنبيه تقني حرج: تعذر تطهير أو إعادة بناء الجداول: {e}")

if __name__ == "__main__":
    # تنفيذ إجراءات التنظيف وإعادة البناء الشامل قبل تشغيل السيرفر
    initialize_sovereignty()
    
    # تحديد المنفذ الخاص ببيئة Railway
    port = int(os.environ.get("PORT", 5000))
    
    # تشغيل محرك المنصة بنجاح
    app.run(host='0.0.0.0', port=port, debug=False)
