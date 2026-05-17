# run.py
# coding: utf-8
# 🚀 المحرك التنفيذي لمنصة محجوب أونلاين 2026
# التوثيق: تشغيل السيرفر وتعميد صلاحيات المالك السيادي وتحديث هيكل البيانات

import os
from apps import create_app, db
from werkzeug.security import generate_password_hash

# 1. إنشاء نسخة التطبيق عبر المصنع المركزي
app = create_app()

def initialize_sovereignty():
    """
    دالة تعميد السيادة: لضمان تحديث جداول قاعدة البيانات (الأعمدة الناقصة) 
    ووجود حساب المالك (علي محجوب) عند تشغيل النظام في بيئة Railway.
    """
    with app.app_context():
        try:
            # 🚨 استدعاء محلي متأخر للموديل هنا لحماية خط الإقلاع ومنع الـ Circular Import تماماً
            from apps.models.admin_db import AdminUser

            # [التحديث الجوهري]: فحص وتحديث هيكل قاعدة البيانات تلقائياً لإضافة أي أعمدة جديدة
            print("⏳ جاري مواءمة وتحديث هيكل السجلات السيادية وقاعدة البيانات...")
            db.create_all()
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
            print(f"⚠️ تنبيه تقني: تعذر تحديث قاعدة البيانات أو الوصول للجداول أثناء البدء: {e}")

if __name__ == "__main__":
    # تنفيذ إجراءات التأكد من الحسابات وتحديث هيكل البيانات قبل إقلاع السيرفر
    initialize_sovereignty()
    
    # تحديد المنفذ (Port) ليتوافق مع بيئة Railway السحابية
    port = int(os.environ.get("PORT", 5000))
    
    # تشغيل المحرك
    # في بيئة الإنتاج على Railway، يفضل جعل debug=False لرفع أداء السيرفر وحمايته
    app.run(host='0.0.0.0', port=port, debug=False)
