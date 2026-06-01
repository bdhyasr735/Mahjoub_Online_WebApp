import sys
import os

# إضافة المجلد الحالي للمسارات لضمان رؤية المجلدات الفرعية
sys.path.append(os.getcwd())

# استيراد 'app' من ملف run.py
from run import app

# Vercel يحتاج كائن يسمى 'app'
