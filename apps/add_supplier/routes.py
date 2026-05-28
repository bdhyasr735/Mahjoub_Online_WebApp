# coding: utf-8
# 🛡️ معالج الموردين - منصة محجوب أونلاين 2026

from flask import Blueprint, render_template, request, jsonify
from Crypto.Cipher import AES
import base64
import json

# افترض أن لديك موديل لقاعدة البيانات
# from models import db, Supplier 

add_supplier = Blueprint('add_supplier', __name__, template_folder='templates')

# مفتاح التشفير (يجب أن يطابق المستخدم في الفرونت إند)
SECRET_KEY = "SECRET_KEY_2026" 

@add_supplier.route('/add_supplier', methods=['GET'])
def add_supplier_page():
    """عرض نموذج تعميد المورد"""
    return render_template('admin/add_supplier.html')

@add_supplier.route('/add_supplier_submit', methods=['POST'])
def add_supplier_submit():
    """استلام، فك تشفير، وحفظ بيانات المورد"""
    try:
        encrypted_data = request.form.get('full_encrypted_data')
        
        if not encrypted_data:
            return jsonify({"status": "error", "message": "لا توجد بيانات للإرسال"}), 400

        # فك التشفير (AES)
        # ملاحظة: هذا مثال بسيط لفك التشفير؛ يفضل استخدام مكتبة متوافقة بالكامل مع CryptoJS
        # هنا نفترض أن البيانات مشفرة وتستقبل كـ String مشفر بـ Base64
        decrypted_raw = encrypted_data # في الحالة الحقيقية ستحتاج لعملية Decrypt متوافقة
        
        # تحويل البيانات إلى قاموس (Dictionary)
        # data = json.loads(decrypted_json)
        
        # مثال لطباعة البيانات بعد فكها للتحقق (لا تتركها في الإنتاج)
        print(f"📦 بيانات المورد المستلمة: {encrypted_data}")

        # هنا تضع كود الحفظ في قاعدة البيانات:
        # new_supplier = Supplier(
        #     name=data['owner_name'],
        #     phone=data['owner_phone'],
        #     shop_id=data['shop_number'],
        #     ...
        # )
        # db.session.add(new_supplier)
        # db.session.commit()

        return jsonify({
            "status": "success", 
            "message": "تم تعميد المورد وحفظ بياناته المشفرة بنجاح في السجل السيادي."
        })

    except Exception as e:
        print(f"❌ خطأ في معالجة طلب المورد: {str(e)}")
        return jsonify({"status": "error", "message": "تعذر حفظ البيانات، يرجى مراجعة سجلات النظام"}), 500
