from flask import current_app # لاستيراد الإعدادات من Flask

def send_whatsapp_otp(phone, otp):
    """إرسال الرمز عبر الواتساب باستخدام الإعدادات المركزية"""
    
    # سحب الإعدادات من كائن الـ Config الخاص بالتطبيق
    phone_number_id = current_app.config.get('WHATSAPP_PHONE_NUMBER_ID')
    access_token = current_app.config.get('WHATSAPP_ACCESS_TOKEN')
    
    if not access_token:
        print("خطأ: لم يتم العثور على WHATSAPP_ACCESS_TOKEN في الإعدادات")
        return False

    api_url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template",
        "template": {
            "name": "otp_verification_template", # تأكد أن هذا الاسم يطابق القالب المعتمد في Meta
            "language": {"code": "ar"},
            "components": [{"type": "body", "parameters": [{"type": "text", "text": otp}]}]
        }
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(f"Error in WhatsApp API: {e}")
        return False
