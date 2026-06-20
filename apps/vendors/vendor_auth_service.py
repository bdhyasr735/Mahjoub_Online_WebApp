# 📂 apps/vendors/vendor_auth_service.py
import requests

def send_whatsapp_otp(phone, otp_code):
    """إرسال الرمز عبر خدمة TextMeBot (معدل للعمل مع مفتاحك)"""
    
    # مفتاحك الشخصي من TextMeBot
    api_key = "rb3tZFnHRcsN" 
    
    # نص الرسالة
    message = f"رمز التحقق الخاص بك في محجوب أونلاين هو: {otp_code}"
    
    # الرابط الخاص بـ TextMeBot
    url = "http://api.textmebot.com/send.php"
    
    # المعاملات كما يتطلبها الـ API الخاص بهم
    params = {
        "recipient": phone, 
        "apikey": api_key,
        "text": message
    }
    
    try:
        # إرسال الطلب
        response = requests.get(url, params=params)
        
        # طباعة النتيجة في Logs للتأكد
        print(f"DEBUG: TextMeBot Response: {response.status_code}, {response.text}")
        
        # TextMeBot يعيد عادة 200 إذا تم قبول الطلب
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: Failed to send via TextMeBot: {e}")
        return False
