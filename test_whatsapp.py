import os
import json
import requests
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env الموجود في جذر المشروع
load_dotenv()

PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERSION = os.getenv("VERSION", "v18.0")
BASE_URL = os.getenv("BASE_URL", "https://graph.facebook.com")

# 📞 تم تحديث الرقم إلى +967779077746 (الصيغة الدولية)
TEST_PHONE_NUMBER = "+967779077746"

def send_test_text_message():
    """
    دالة لإرسال رسالة نصية عادية للاختبار.
    """
    if not PHONE_NUMBER_ID or not ACCESS_TOKEN:
        print("❌ خطأ: تأكد من وجود PHONE_NUMBER_ID و ACCESS_TOKEN في ملف .env")
        return

    url = f"{BASE_URL}/{VERSION}/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": TEST_PHONE_NUMBER,
        "type": "text",
        "text": {
            "body": "🚀 مرحباً! هذه رسالة اختبارية تؤكد أن سيرفر محوب أونلاين متصل بـ واتساب API بنجاح 100%!"
        }
    }
    
    try:
        print("⏳ جاري إرسال رسالة الاختبار...")
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()
        
        if response.status_code == 200:
            print("✅ تم إرسال الرسالة بنجاح! تحقق من هاتفك.")
        else:
            print("❌ فشل الإرسال، تحقق من الرد أدناه:")
        
        print("\n📩 نتيجة الاستجابة من ميتا:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ خطأ في الاتصال بالخادم: {e}")

if __name__ == "__main__":
    send_test_text_message()
