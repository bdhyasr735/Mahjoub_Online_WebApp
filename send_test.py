# coding: utf-8
import requests

# رابط تطبيقك على منصة رندر مع مسار إرسال الرسائل
url = "https://mahjoub-online-webapp-1-f0lj.onrender.com/admin/whatsapp/api/send-message"

# بيانات الرسالة والرقم المستهدف
payload = {
    "recipient_number": "96779077746",
    "message": "مرحباً! هذه رسالة تجريبية من السكريبت البرمجي لمحجوب أونلاين."
}

# إرسال الطلب
try:
    response = requests.post(url, json=payload)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Error:", str(e))
