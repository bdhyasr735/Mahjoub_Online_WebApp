import sys
import os

# إضافة المجلد الرئيسي للمشروع لمسار النظام ليتمكن من رؤية مجلد 'apps'
sys.path.append(os.getcwd())

from apps import create_app

# Vercel يحتاج لمتغير يسمى 'app' ليقوم بتشغيله
app = create_app()
