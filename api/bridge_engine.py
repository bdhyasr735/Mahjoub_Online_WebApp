# 📂 api/bridge_engine.py
# محرك الإرسال السيادي - Bridge Engine

import os
from whatsapp_web_python import WhatsApp

class BridgeEngine:
    def __init__(self, session_name="sovereign_session"):
        self.bot = WhatsApp(session=session_name)

    def dispatch(self, phone, message):
        """إرسال الرسالة مباشرة عبر الواتساب المرتبط"""
        try:
            # تنظيف الرقم من أي رموز غير مرغوب فيها
            clean_phone = str(phone).replace("+", "").replace(" ", "")
            self.bot.send_message(clean_phone, message)
            return True, "تم الإرسال بنجاح"
        except Exception as e:
            return False, str(e)

# تهيئة المحرك كـ Singleton ليتم استخدامه في كامل التطبيق
engine = BridgeEngine()
