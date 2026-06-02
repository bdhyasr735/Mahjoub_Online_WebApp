📊 [المجلد الرئيسي للمشروع]
├── api/
│   └── index.py          <-- الملف الحالي (نقطة انطلاق Vercel)
├── apps/
│   ├── __init__.py       <-- مصنع التطبيق المركزي الذي جهزناه معاً
│   ├── extensions.py     <-- كبسولة الملحقات المعزولة
│   ├── auth_portal/      <-- بوابة النفاذ السيادية (Blueprints & Routes)
│   └── models/           <-- موديلات قواعد البيانات (admin_db, wallet_db...)
├── vercel.json           <-- ملف حوكمة التوجيه والنشر
└── requirements.txt      <-- ملف المكتبات (يجب أن يحتوي على Flask و Flask-SQLAlchemy وغيرها)
