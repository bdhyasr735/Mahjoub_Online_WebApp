# 📂 test_whatsapp.py
import os
import requests
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env إذا كان موجوداً محلياً
load_dotenv()

def send_test_whatsapp():
    token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
    api_version = os.environ.get('WHATSAPP_API_VERSION', 'v20.0')
    target_phone = "967779077746"

    print(f"\n🔍 [Check] Phone ID: {phone_id} | Token Status: {'✅ Present' if token else '❌ Missing'}")

    if not token or not phone_id:
        print("❌ [Error]: متغيرات الواتساب (Token أو Phone ID) مفقودة تماماً في البيئة الحالية.")
        print("💡 تأكد من إضافتها في ملف .env أو في إعدادات المنصة (Render Environment Variables).")
        return

    url = f"https://graph.facebook.com/{api_version}/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": target_phone,
        "type": "template",
        "template": {
            "name": "hello_world",
            "language": {"code": "en_US"}
        }
    }

    try:
        print("🚀 جاري إرسال الطلب إلى خوادم Meta...")
        res = requests.post(url, json=payload, headers=headers)
        print(f"\n📩 [Meta Status Code]: {res.status_code}")
        print(f"📩 [Meta API Response]: {res.text}\n")
    except Exception as e:
        print(f"❌ [Connection Error]: فشل الاتصال بخدمة Meta: {e}")

if __name__ == '__main__':
    send_test_whatsapp()
