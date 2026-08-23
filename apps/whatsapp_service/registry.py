# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/registry.py

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from apps.whatsapp_service.whatsapp_api import WhatsAppAPI

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "bi-whatsapp"
SHOW_IN_ADMIN = True

# روابط الموديول التي ستظهر في القائمة الجانبية لوحة التحكم
LINKS = {
    'whatsapp_service.index': 'إدارة مراسلات الواتساب'
}

# تعريف الـ Blueprint الخاص بموديول الواتساب
whatsapp_bp = Blueprint(
    'whatsapp_service', 
    __name__, 
    template_folder='templates',
    static_folder='static'
)

@whatsapp_bp.route('/')
@login_required
def index():
    """عرض لوحة تحكم مراسلات الواتساب"""
    return render_template('whatsapp_service/index.html')

@whatsapp_bp.route('/api/send', methods=['POST'])
@login_required
def api_send_message():
    """نقطة نهاية (API) لإرسال الرسائل باستخدام كلاس WhatsAppAPI"""
    data = request.get_json() or {}
    recipient = data.get('phone')
    message = data.get('message')
    
    if not recipient or not message:
        return jsonify({"success": False, "error": "رقم الهاتف ونص الرسالة مطلوبان"}), 400
        
    # استدعاء الكلاس الذي قمت بتوفير مسبقاً
    wa = WhatsAppAPI()
    result = wa.send_text_message(recipient, message)
    
    if result.get("success"):
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@whatsapp_bp.route('/api/test', methods=['GET'])
@login_required
def api_test_connection():
    """اختبار الاتصال مع Meta WhatsApp API"""
    wa = WhatsAppAPI()
    is_connected = wa.test_connection()
    return jsonify({"connected": is_connected})

def register_module(app):
    """دالة التسجيل التلقائي في النظام"""
    if 'whatsapp_service' not in app.blueprints:
        app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
