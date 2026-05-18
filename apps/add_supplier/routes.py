import os
import random
import string
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename

# 👑 إنشاء الـ Blueprint الخاص بحوكمة الموردين وضخ المعرفات
admin_suppliers = Blueprint(
    'admin_suppliers', 
    __name__, 
    template_folder='templates',
    static_folder='static'
)

# تعيين الامتدادات المسموح برفعها لصور الوثائق الرسمية
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_sovereign_id():
    """توليد معرف سيادي فريد للمورد متوافق مع نظام التنبؤ بالواجهة"""
    random_digits = ''.join(random.choices(string.digits, k=3))
    return f"SUP-MAH{random_digits}"

def generate_wallet_code():
    """توليد كود محفظة آلية تابعة للمورد تلقائياً"""
    random_digits = ''.join(random.choices(string.digits, k=3))
    return f"WEL-MAH{random_digits}"


@admin_suppliers.route('/admin/suppliers/add', methods=['GET', 'POST'])
def add_supplier_page():
    """مسار عرض استمارة التعميد ومعالجة الضخ المالي والأرشفة"""
    
    if request.method == 'POST':
        try:
            # 1. سحب بيانات الوصول والتوثيق الأمنية
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            identity_type = request.form.get('identity_type', '').strip()
            identity_number = request.form.get('identity_number', '').strip()
            
            # 2. سحب بيانات المالك والمنشأة الجغرافية
            owner_name = request.form.get('owner_name', '').strip()
            trade_name = request.form.get('trade_name', '').strip()
            owner_phone = request.form.get('owner_phone', '').strip()
            shop_phone = request.form.get('shop_phone', '').strip()  # اختياري الآن
            province = request.form.get('province', '').strip()
            district = request.form.get('district', '').strip()
            address_detail = request.form.get('address_detail', '').strip()
            
            # 3. سحب قنوات الصرف المالي وفئة النشاط
            fin_type = request.form.get('fin_type', '').strip()
            bank_name = request.form.get('bank_name', '').strip()
            bank_acc = request.form.get('bank_acc', '').strip()
            activity_type = request.form.get('activity_type', '').strip()

            # 4. التوليد الديناميكي للمعرفات السيادية والمحفظة الآلية
            sovereign_id = generate_sovereign_id()
            wallet_code = generate_wallet_code()

            # 5. معالجة رفع صورة الوثيقة الرسمية إن وجدت بأمان
            identity_image_path = None
            if 'identity_image' in request.files:
                file = request.files['identity_image']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # دمج المعرف الفريد مع الاسم لقطع دابر التداخل في السيرفر السحابي
                    unique_filename = f"{sovereign_id}_{filename}"
                    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads/identities')
                    
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder, exist_ok=True)
                        
                    file.save(os.path.join(upload_folder, unique_filename))
                    identity_image_path = f"uploads/identities/{unique_filename}"

            # 🛡️ [هنا يتم ربط وتمرير البيانات لقاعدة البيانات أو محرك المايكرو-إنجين]
            # مثال على هيكلية الحفظ المتوقعة:
            # supplier_data = {
            #     "sovereign_id": sovereign_id, "wallet_code": wallet_code, "username": username,
            #     "identity_type": identity_type, "identity_number": identity_number, "owner_name": owner_name,
            #     "trade_name": trade_name, "owner_phone": owner_phone, "shop_phone": shop_phone,
            #     "province": province, "district": district, "address_detail": address_detail,
            #     "fin_type": fin_type, "bank_name": bank_name, "bank_acc": bank_acc, "activity_type": activity_type,
            #     "identity_image": identity_image_path, "status": "active"
            # }

            # 👑 صياغة الرد الاستجابي النهائي لـ AJAX لتشغيل الـ Modal بنجاح ساحق
            return jsonify({
                "status": "success",
                "message": "تم تعميد المورد وإنشاء المحفظة بنجاح وتوثيق الهوية السيادية.",
                "data": {
                    "sovereign_id": sovereign_id,
                    "wallet_code": wallet_code
                }
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"انهيار خط معالجة السيرفر: {str(e)}"
            }), 500

    # في حالة طلب الصفحة عبر GET: تقديم لواجهة الإدخال مع توفير الـ Tokens الأمنية الاحتياطية
    return render_template('admin/add_supplier.html', backup_csrf="MAHJOUB_SECURE_TOKEN_2026")


@admin_suppliers.route('/admin/suppliers/check-duplicate', methods=['GET'])
def check_duplicate():
    """🛡️ محرك التوثيق اللحظي الحامي من تكرار المعرفات وقنوات الاتصال الحيوية"""
    check_type = request.args.get('type', '').strip()
    value = request.args.get('value', '').strip()

    if not check_type or not value:
        return jsonify({"exists": False, "error": "Missing parameters"}), 400

    # هنا يتم الربط البرمجي مع قاعدة البيانات المحددة للتحقق من التكرار
    # سنضع الافتراض المبدئي False لضمان استمرار عمل الواجهة ومرونة تجاربك البرمجية الحالية
    exists = False

    # هيكلية الفحص المنطقي:
    # if check_type == 'username':
    #     exists = db.suppliers.find_one({"username": value}) is not None
    # elif check_type == 'identity_number':
    #     exists = db.suppliers.find_one({"identity_number": value}) is not None
    # ... وهكذا لبقية الحقول

    return jsonify({"exists": exists})
