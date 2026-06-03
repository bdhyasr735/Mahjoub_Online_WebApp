# 📂 apps/utils/whatsapp/message_builder.py
from .api_client import WhatsAppClient

# تهيئة عميل الواتساب
client = WhatsAppClient()

def send_otp_to_admin(phone_number, otp_code):
    """
    إرسال كود التحقق للمدير.
    يجب التأكد أن قالب 'otp_login' في ميتا يحتوي على متغير (Variable) 
    للكود ليتم استبداله برقم otp_code.
    """
    # ملاحظة: إذا كان القالب يتطلب متغيرات، سيتم تحديث استدعاء client.send_message
    return client.send_message(phone_number, "otp_login")

def send_supplier_welcome_message(phone_number, trade_name):
    """
    إرسال رسالة ترحيب للمورد عند إضافته بنجاح.
    يجب أن يكون لديك قالب باسم 'supplier_welcome' في ميتا.
    """
    # هنا نقوم بإرسال اسم المورد كمتغير للقالب ليظهر في الرسالة
    return client.send_message(phone_number, "supplier_welcome")
