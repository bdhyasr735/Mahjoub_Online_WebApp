import os
import sys

# إضافة المجلد الرئيسي إلى مسار بايثون ليتمكن من استيراد apps
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run import app

# Vercel يحتاج لمتغير باسم app
