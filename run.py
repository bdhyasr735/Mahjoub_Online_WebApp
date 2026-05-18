# coding: utf-8
# 🚀 المحرك التنفيذي وفرمان الحوكمة الشاملة لمنصة محجوب أونلاين 2026

import os
from apps import create_app, db
from werkzeug.security import generate_password_hash

# 1. إنشاء نسخة التطبيق عبر المصنع المركزي الشامل
app = create_app()

def audit_and_verify_routes():
    """
    🛡️ حارس المسارات: يقوم بفحص كافة الروابط والـ Blueprints المسجلة في النواة
    عند الإقلاع للتأكد من عدم وجود تضارب يسبب انهيار الـ Dashboard أو 500 Error.
    """
    print("\n🔍 --- جاري مراجعة وتدقيق خريطة المسارات السيادية للتطبيق ---")
    active_endpoints = []
    for rule in app.url_map.iter_rules():
        active_endpoints.append(rule.endpoint)
        # طباعة المسارات الحيوية للتأكد من تسجيلها
        if 'admin_' in rule.endpoint or 'supplier' in rule.endpoint:
            print(f"📍 مسار نشط ومعمد بنجاح -> Endpoint: {rule.endpoint} | Path: {rule}")
            
    # التحقق الاستباقي لقطع دابر الـ BuildError
    required_endpoints = ['admin_suppliers.add_supplier_page']
    for ep in required_endpoints:
        if ep not in active_endpoints:
            print(f"⚠️ تحذير حرج: الـ Endpoint '{ep}' غير مسجل! راجع ملف التسجيل في apps/__init__.py")
    print("✨ --- تم الانتهاء من تدقيق خريطة الروابط بنجاح مطلق ---\n")


def initialize_sovereignty():
    """
    دالة تعميد وتشييد البنية التحتية لعام 2026:
    تقوم بإنشاء كافة الجداول الناقصة مباشرة داخل سيرفر PostgreSQL الحي.
    """
    with app.app_context():
        try:
            print("⏳ جاري فحص وتعميد جداول النواة في السيرفر الحي (PostgreSQL)...")
            
            # أمر التشييد الشامل والسيادي لجميع الجداول المستدعاة في الـ __init__
            db.create_all()
            db.session.commit()
            print("🚀 سيادة وحوكمة: تم فحص قاعدة البيانات وإنشاء الجداول بنجاح تنفيذي مطلق.")
            
            # تأمين حساب المؤسس والمالك السيادي للمنصة
            from apps.models.admin_db import AdminUser
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
                
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ تنبيه تقني حرج: تعذر إنشاء الجداول على السيرفر الحي: {e}")

if __name__ == "__main__":
    # 1. تنفيذ فحص المسارات لقطع دابر انهيار التطبيقات المشتركة
    audit_and_verify_routes()
    
    # 2. تنفيذ الفحص والإنشاء الآمن لقاعدة البيانات
    initialize_sovereignty()
    
    # 3. تحديد المنفذ الخاص ببيئة رفعه على السحاب (Railway)
    port = int(os.environ.get("PORT", 5000))
    
    # 4. تشغيل محرك المنصة بقوة وثبات وبدون Debug لتأمين الإنتاجية
    print(f"🌐 إطلاق منصة محجوب أونلاين على الرابط المحلي: http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
