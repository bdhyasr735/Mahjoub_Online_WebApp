import sys
import os

# إضافة المسار الحالي للمشروع إلى مسار البحث عن المكتبات
# هذا يجعل مجلد 'apps' مرئياً كجزء من بيئة بايثون
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# استيراد التطبيق من ملف run.py الموجود في المجلد الرئيسي
from run import app

# Vercel يحدد هذا المتغير كـ Entrypoint
