from core import create_app, db
from flask_migrate import Migrate

# 1. إنشاء نسخة التطبيق من خلال دالة البناء في النواة (core)
# هذه الدالة تقوم بتسجيل بوابات الإدارة (Blueprints) وربط قاعدة البيانات
app = create_app()

# 2. إعداد نظام المهاجرة (Migrate) لربط الموديلات (User, Supplier, Product) 
# وضمان مزامنة الجداول مع قاعدة البيانات في بيئة Render
migrate = Migrate(app, db)

if __name__ == '__main__':
    """
    تشغيل المحرك الرقمي لمنصة محجوب أونلاين.
    يتم التفعيل هنا لضمان عمل كافة الأدوات والروابط والتحقق من الهوية.
    """
    # تفعيل وضع التصحيح (Debug) لرصد التغييرات فوراً أثناء بناء المرحلة الثانية
    app.run(debug=True)
