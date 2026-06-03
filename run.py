# coding: utf-8
# 📂 run.py - الحارس الأمني للتشغيل (نظام الاستمرارية المطلقة)

import os
import time
import sys
from apps import create_app

def start_server():
    try:
        # إنشاء التطبيق
        app = create_app()
        port = int(os.environ.get("PORT", 10000))
        
        print(f"🚀 السيرفر يعمل الآن على المنفذ: {port}")
        app.run(host="0.0.0.0", port=port)
        
    except Exception as e:
        # هذه المنطقة هي "الملاذ الأخير"
        # إذا حدث خطأ حرج، لا نغلق السيرفر، بل ننتظر ونحاول مجدداً
        print(f"🚨 خطأ حرج في النظام: {e}")
        print("🛡️ الحارس الأمني: السيرفر سيحاول إعادة التشغيل خلال 5 ثوانٍ...")
        time.sleep(5)
        # إعادة محاولة التشغيل للحفاظ على السيرفر حياً
        start_server()

if __name__ == "__main__":
    start_server()
