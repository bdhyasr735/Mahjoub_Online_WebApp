import sys
import os

# إضافة المسار الحالي لكي يرى المترجم مجلد apps
sys.path.append(os.getcwd())

# استيراد كائن التطبيق من run.py
from run import app

# Vercel يحتاج أن يكون المتغير 'app' معرفاً في هذا الملف
