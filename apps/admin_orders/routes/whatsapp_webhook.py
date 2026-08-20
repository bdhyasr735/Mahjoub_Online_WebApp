import os
from flask import request, jsonify, Blueprint

# إنشاء بلو برنت (Blueprint) لهذا الملف
webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    # ميتا ترسل هذا الطلب للتحقق
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    # تطابق مع VERIFY_TOKEN الموجود في ملف .env
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
