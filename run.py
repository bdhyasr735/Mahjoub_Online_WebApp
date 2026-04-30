import os
from core import create_app, db
from flask_migrate import Migrate

# إنشاء التطبيق من النواة
app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    # جلب البورت من متغيرات البيئة (خاص بـ Railway) 
    # وإذا لم يوجد (محلياً) يستخدم 5000 كافتراضي
    port = int(os.environ.get("PORT", 5000))
    
    # تشغيل السيرفر مع ضبط المضيف والبورت بشكل ديناميكي
    # المضيف 0.0.0.0 ضروري لكي يتمكن Railway من توجيه الترافيك للسيرفر
    app.run(host='0.0.0.0', port=port)
