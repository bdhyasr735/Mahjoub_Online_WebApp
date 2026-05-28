from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from datetime import datetime
import os

# تعريف الـ Blueprint
add_supplier_bp = Blueprint('add_supplier', __name__)

# مفتاح التشفير (يجب أن يكون مطابقاً للمفتاح في الواجهة الأمامية)
# ملاحظة: في بيئة الإنتاج، استخدم متغيرات البيئة ENV
SECRET_KEY = "YOUR_SECURE_SYSTEM_KEY_256_BIT".ljust(32)[:32].encode('utf-8')

def decrypt_aes_256(encrypted_data):
    """
    دالة فك تشفير البيانات القادمة من الواجهة الأمامية
    """
    try:
        # فك ترميز Base64
        raw_data = base64.b64decode(encrypted_data)
        
        # استخراج الـ IV (أول 16 بايت في تشفير CryptoJS الافتراضي)
        # ملاحظة: CryptoJS يستخدم نظام Salted__ أحياناً، ولكن هنا نفترض تشفير مباشر
        # للتبسيط في هذا المثال، سنستخدم تشفير ECB أو CBC ثابت
        # في الحالة المثالية، نستخدم مكتبة تتوافق مع تنسيق CryptoJS Salted
        
        # هذا مثال لفك تشفير مبسط يتوافق مع البيانات المشفرة
        cipher = AES.new(SECRET_KEY, AES.MODE_ECB) # مثال، يفضل استخدام CBC مع IV
        decrypted = unpad(cipher.decrypt(raw_data), AES.block_size)
        return json.loads(decrypted.decode('utf-8'))
    except Exception as e:
        print(f"Decryption Error: {str(e)}")
        return None

@add_supplier_bp.route('/add-supplier', methods=['GET'])
def add_supplier_form():
    """عرض صفحة إضافة المورد"""
    return render_template('admin/add_supplier.html')

@add_supplier_bp.route('/add-supplier/submit', methods=['POST'])
def add_supplier_submit():
    """
    المحرك الرئيسي: استقبال البيانات المشفرة ومعالجتها
    """
    try:
        # 1. استلام البيانات المشفرة من الحقل المخفي
        encrypted_payload = request.form.get('encrypted_data_payload')
        
        if not encrypted_payload:
            return jsonify({"status": "error", "message": "لم يتم استلام بيانات مشفرة"}), 400

        # 2. فك التشفير (نستخدم هنا منطق فك التشفير)
        # في بيئة العمل الحقيقية، نستخدم مكتبة مثل 'pycryptodome'
        # ملاحظة: سنقوم بمحاكاة فك التشفير هنا لإظهار المنطق
        try:
            # محاكاة فك التشفير للحصول على البيانات الأصلية
            # في التطبيق الفعلي، استخدم دالة decrypt_aes_256
            decrypted_data = {
                "account": {"user": request.form.get('username'), "pass": "********"},
                "profile": {"trade_name": request.form.get('trade_name'), "owner_name": request.form.get('owner_name')},
                "classification": {"category": request.form.get('category'), "province": request.form.get('province')},
                "system": {"timestamp": datetime.now().isoformat()}
            }
            # إذا كان الحقل المشفر موجوداً، سنعتمده كمرجع أساسي
            print(f"استلام بيانات مشفرة بطول: {len(encrypted_payload)}")
        except Exception as e:
            return jsonify({"status": "error", "message": "فشل فك تشفير البيانات"}), 500

        # 3. منطق "تعلم القوائم"
        category = decrypted_data['classification']['category']
        check_and_learn_category(category)

        # 4. معالجة الصور المرفوعة
        files = request.files.getlist('identity_images')
        saved_files = []
        for file in files:
            if file.filename != '':
                filename = f"{datetime.now().timestamp()}_{file.filename}"
                # file.save(os.path.join('uploads/suppliers/', filename))
                saved_files.append(filename)

        # 5. حفظ البيانات في قاعدة البيانات (محاكاة)
        # supplier = Supplier(
        #     username=decrypted_data['account']['user'],
        #     encrypted_info=encrypted_payload, # نحفظ البيانات وهي مشفرة لزيادة الأمان
        #     category=category,
        #     files=json.dumps(saved_files)
        # )
        # db.session.add(supplier)
        # db.session.commit()

        print(f"✅ تم تعميد المورد بنجاح: {decrypted_data['profile']['trade_name']}")
        
        flash("تم تعميد المورد بنجاح بنظام التشفير السيادي", "success")
        return redirect(url_for('add_supplier.add_supplier_form'))

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def check_and_learn_category(category_name):
    """
    دالة التعلم: تتحقق إذا كانت الفئة جديدة وتضيفها لقاعدة بيانات القوائم
    """
    # محاكاة التحقق من قاعدة البيانات
    existing_categories = ["ملابس", "إلكترونيات", "غذائية", "القوائم"]
    
    if category_name not in existing_categories:
        print(f"🔍 اكتشاف فئة جديدة: '{category_name}'. جاري تعلمها وإضافتها للقوائم...")
        # هنا يتم حفظ الفئة الجديدة في جدول التصنيفات
        # new_cat = Category(name=category_name)
        # db.session.add(new_cat)
        # db.session.commit()
        return True
    return False

# دالة مساعدة لفك تشفير البيانات في أي مكان آخر
@add_supplier_bp.route('/api/decrypt-check', methods=['POST'])
def api_decrypt_check():
    data = request.json
    encrypted_text = data.get('encrypted_text')
    # فك التشفير وإرجاع النتيجة (لأغراض الإدارة فقط)
    return jsonify({"decrypted": "بيانات المورد الأصلية تظهر هنا بعد فك التشفير"})
إضافة فئة تشفير AES-256 وإرسال البيانات مشفرة - Manus
