# coding: utf-8
# 🚀 المحرك التنفيذي لمنصة محجوب أونلاين 2026
# التوثيق: تشغيل السيرفر وتعميد صلاحيات المالك السيادي

import os
from apps import create_app, db
from apps.models.admin_db import AdminUser
from werkzeug.security import generate_password_hash

# 1. إنشاء نسخة التطبيق عبر المصنع المركزي
app = create_app()

def initialize_sovereignty():
    """
    دالة تعميد السيادة: لضمان وجود حساب المالك (علي محجوب)
    عند تشغيل النظام لأول مرة أو بعد تحديث قاعدة البيانات.
    """
    with app.app_context():
        try:
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
            print(f"⚠️ تنبيه تقني: تعذر الوصول لجداول المستخدمين أثناء البدء: {e}")

if __name__ == "__main__":
    # تنفيذ إجراءات التأكد من الحسابات قبل إقلاع السيرفر
    initialize_sovereignty()
    
    # تحديد المنفذ (Port) ليتوافق مع بيئة Railway السحابية
    port = int(os.environ.get("PORT", 5000))
    
    # تشغيل المحرك
    # ملاحظة: debug=True تستخدم للتطوير، وفي الإنتاج يفضل إيقافها
    app.run(host='0.0.0.0', port=port, debug=True)
