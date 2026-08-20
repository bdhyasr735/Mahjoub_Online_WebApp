import os
import json
import requests
from flask import request, jsonify, Blueprint

# إنشاء بلو برنت (Blueprint) لهذا الملف
webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    # ميتا ترسل هذا الطلب للتحقق
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    # تطابق مع VERIFY_TOKEN الموجود في ملف .env أو متغيرات البيئة في السحابة
    if mode and token and token == os.getenv('VERIFY_TOKEN'):
        return challenge, 200
    return 'فشل التحقق', 403

@webhook_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    # استقبال البيانات من ميتا (حالة وصول الرسالة أو رد العميل)
    data = request.json
    print("📩 إشعار من واتساب:", data)
    
    # هنا يمكنك إضافة كود لتحديث قاعدة بيانات المتجر
    # إذا كان العميل قد قرأ الفاتورة، قم بتحديث الطلب إلى "تم الاستلام"
    
    return "OK", 200

# ============================================================
# 🚀 تم إضافة هذا المسار الجديد للاختبار عبر المتصفح (بدون Terminal)
# ============================================================
@webhook_bp.route('/test-whatsapp')
def trigger_test_message():
    """
    مسار اختبار. بمجرد فتح هذا الرابط في المتصفح بعد الرفع، سيتم إرسال رسالة.
    """
    try:
        # قراءة المتغيرات من بيئة السحابة
        phone_number_id = os.getenv('PHONE_NUMBER_ID')
        access_token = os.getenv('ACCESS_TOKEN')
        test_phone = "+967779077746"  # 👈 الرقم الذي تريد إرسال رسالة الاختبار إليه

        if not phone_number_id or not access_token:
            return "❌ خطأ: تأكد من إعداد PHONE_NUMBER_ID و ACCESS_TOKEN في متغيرات بيئة السيرفر."

        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # إرسال رسالة نصية عادية (Text) - وهي الأفضل للاختبار
        data = {
            "messaging_product": "whatsapp",
            "to": test_phone,
            "type": "text",
            "text": {
                "body": "🚀 نجاح! السيرفر متصل ويعمل، والربط مع واتساب API تم بنجاح 100%."
            }
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        # عرض النتيجة في المتصفح
        return f"""
        <h2>📨 اختبار إرسال الرسالة</h2>
        <p><strong>الحالة:</strong> {'✅ تم الإرسال بنجاح! تحقق من هاتفك.' if response.status_code == 200 else '❌ فشل الإرسال'}</p>
        <p><strong>رد ميتا (JSON):</strong></p>
        <pre>{json.dumps(result, indent=2, ensure_ascii=False)}</pre>
        """
        
    except Exception as e:
        return f"❌ حدث خطأ تقني في السيرفر: {str(e)}"
