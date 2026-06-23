import time  # تأكد من إضافة هذه المكتبة في الأعلى

@staticmethod
def initiate_login(phone, otp_code):
    clean_phone = re.sub(r'[^\d]', '', str(phone))
    api_key = os.environ.get('TEXTMEBOT_API_KEY', 'rb3tZFnHRcsN')
    
    message = f"Mahjoub Online | Security Code\n\nرمز التحقق هو: {otp_code}\n— محجوب أونلاين"
    base_url = "http://api.textmebot.com/send.php"
    
    params = {"recipient": clean_phone, "apikey": api_key, "text": message, "json": "yes"}
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=15)
        data = response.json() if response.status_code == 200 else {}
        
        # إذا طلب الخدمة تأخيراً (8 ثوانٍ)
        if response.status_code == 403 and "Delay needed" in str(response.text):
            print("⚠️ [System] تم اكتشاف تأخير من TextMeBot، ننتظر 10 ثوانٍ...")
            time.sleep(10) # انتظر 10 ثوانٍ برمجياً
            # محاولة ثانية واحدة فقط
            response = requests.get(base_url, params=params, headers=headers, timeout=15)
        
        print(f"DEBUG [TextMeBot Response]: {response.status_code} - {response.text}")
        return response.status_code == 200
            
    except Exception as e:
        print(f"CRITICAL [TextMeBot Error]: {str(e)}")
        return False
