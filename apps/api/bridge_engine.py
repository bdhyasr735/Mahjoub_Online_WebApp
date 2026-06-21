# 📂 apps/api/bridge_engine.py

from apps.models.otp_db import OTPLog
from apps.extensions import db

# ... داخل دالة dispatch ...
def dispatch(self, phone, message, otp_log_id=None):
    # إذا كان هناك سجل OTP، نحدث حالته
    if otp_log_id:
        log = OTPLog.query.get(otp_log_id)
    
    try:
        self.bot.send_message(phone, message)
        if log:
            log.whatsapp_status = 'sent'
            db.session.commit()
        return True, "تم الإرسال"
    except Exception as e:
        if log:
            log.whatsapp_status = 'failed'
            log.error_msg = str(e)
            db.session.commit()
        return False, str(e)
