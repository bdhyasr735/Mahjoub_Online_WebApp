# run.py
# coding: utf-8
# 🔑 مفتاح تشغيل المحرك المركزي - منصة محجوب أونلاين 2026

import os
from apps import create_app

# إنشاء كائن التطبيق المركزي
app = create_app()

if __name__ == "__main__":
    # جلب المنفذ ديناميكياً لتفادي أي تعارض في بيئات التشغيل
    port = int(os.environ.get('PORT', 5000))
    
    # التشغيل المحلي للمطور (Development) بكفاءة ومرونة كاملة
    print(f"💻 جاري تشغيل السيرفر المحلي لـ (سوقك الذكي) على المنفذ: {port}")
    app.run(debug=True, host='0.0.0.0', port=port)
