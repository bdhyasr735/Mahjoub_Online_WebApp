# coding: utf-8
# 🚀 الجسر السحابي: نقطة الانطلاق الموحدة لـ Vercel - منصة محجوب أونلاين 2026

import sys
import os

# إضافة المجلد الرئيسي للمشروع إلى مسارات النظام (sys.path) 
# لضمان قدرة Vercel على الوصول إلى مجلد "apps" واستيراد create_app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from apps import create_app

# إنشاء كائن التطبيق (Application Factory)
# هذا الكائن "app" هو ما سيبحث عنه Vercel لتشغيل الدوال السحابية
app = create_app()

# ملاحظة: 
# لا تقم بإضافة app.run() هنا، لأن Vercel يدير عملية التشغيل تلقائياً.
# هذا الملف يعمل كـ "Entrypoint" فقط.
