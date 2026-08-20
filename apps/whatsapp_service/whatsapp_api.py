import os
import json
import requests
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env الموجود في جذر المشروع
load_dotenv()

# قراءة البيانات من ملف .env
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERSION = os.getenv("VERSION", "v18.0")
BASE_URL = os.getenv("BASE_URL", "https://graph.facebook.com")

def send_invoice_whatsapp(to_number, order_id, total_price):
    """
    دالة إرسال الفاتورة عبر واتساب باستخدام قالب معتمد مسبقاً.
    """
    if not PHONE_NUMBER_ID or not ACCESS_TOKEN:
        print("❌ خطأ: لم يتم العثور على بيانات الاعتماد (Phone ID أو Token) في ملف .env")
        return {"error": "Missing credentials"}

    # رابط واجهة برمجة التطبيقات (API Endpoint)
    url = f"{BASE_URL}/{VERSION}/{PHONE_NUMBER_ID}/messages"
    
    # رؤوس الطلب (Headers)
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # بيانات القالب
    # 🚨 ملاحظة مهمة جداً: يجب أن يكون 'order_invoice' مطابقاً لاسم القالب الذي أنشأته في ميتا
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": "order_invoice", 
            "language": {"code": "ar"},
            "components": [{
                "type": "body",
                "parameters": [
                    {"type": "text", "text": str(order_id)},
                    {"type": "text", "text": str(total_price)}
                ]
            }]
        }
    }
    
    try:
        # إرسال الطلب
        response = requests.post(url, headers=headers, data=json.dumps(data))
        # إرجاع النتيجة من ميتا لتراها في السيرفر
        return response.json()
    except Exception as e:
        return {"error": str(e)}
