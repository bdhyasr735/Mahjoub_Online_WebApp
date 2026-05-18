import os
import secrets
from flask import Blueprint, render_template, request, jsonify, current_app, url_for
from werkzeug.utils import secure_filename

# 🛡️ تعريف الـ Blueprint الخاص بإضافة وتعميد الموردين
admin_suppliers_bp = Blueprint(
    'admin_suppliers', 
    __name__, 
    template_folder='templates',
    static_folder='static'
)

# ─── محاكاة لقاعدة البيانات (استبدلها بالـ Model الخاص بك في PostgreSQL/SQLAlchemy) ───
# مثال: from apps.models import db, Supplier, Wallet
MOCK_DB = {
    "usernames": ["ali_2026", "admin", "mahjoub_user"],
    "identity_numbers": ["101202303", "404505606"],
    "owner_phones": ["771234567"],
    "trade_names": ["مؤسسة النجاح", "مجموعة البرق"],
    "bank_accounts": ["123456789"]
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ─── المسارات (Routes) ───

@admin_suppliers_bp.route('/admin/suppliers/add', methods=['GET', 'POST'])
def add_supplier_page():
    """
    عرض صفحة تعميد المورد (GET) ومعالجة طلب التعميد السحابي (POST).
    """
    if request.method == 'POST':
        try:
            # 1. استقبال البيانات الأساسية من النموذج
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            identity_type = request.form.get('identity_type', '').strip()
            identity_number = request.form.get('identity_number', '').strip()
            
            owner_name = request.form.get('owner_name', '').strip()
            trade_name = request.form.get('trade_name', '').strip()
            owner_phone = request.form.get('owner_phone', '').strip()
            shop_phone = request.form.get('shop_phone', '').strip()
            
            province = request.form.get('province', '').strip()
            district = request.form.get('district', '').strip()
            address_detail = request.form.get('address_detail', '').strip()
            
            fin_type = request.form.get('fin_type', '').strip()
            bank_name = request.form.get('bank_name', '').strip()
            bank_acc = request.form.get('bank_acc', '').strip()
            activity_type = request.form.get('activity_type', '').strip()

            # 2. التحقق الخلفي الصارم (Backend Validation) من الحقول الإلزامية
            if not all([username, password, identity_type, identity_number, owner_name, trade_name, owner_phone, province, district, address_detail, bank_name, bank_acc]):
                return jsonify({
                    "status": "error",
                    "message": "⚠️ جميع الحقول الإلزامية يجب أن تكون مكتملة وصحيحة هندسيًا."
                }), 400

            # 3. التحقق من عدم التكرار في قاعدة البيانات (خط الدفاع الثاني)
            if username in MOCK_DB["usernames"]:
                return jsonify({"status": "error", "message": "اسم المستخدم هذا محجوز مسبقاً بالتشفير السيادي."}), 400
            if identity_number in MOCK_DB["identity_numbers"]:
                return jsonify({"status": "error", "message": "رقم الوثيقة / الهوية مسجل مسبقاً في النظام."}), 400
            if bank_acc in MOCK_DB["bank_accounts"]:
                return jsonify({"status": "error", "message": "رقم الحساب المالي مرتبط بمورد آخر حالياً."}), 400

            # 4. معالجة رفع صورة الوثيقة (اختياري) وحفظها بأمان
            identity_image_path = None
            if 'identity_image' in request.files:
                file = request.files['identity_image']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # توليد اسم عشوائي فريد لمنع تداخل الملفات
                    unique_filename = f"doc_{secrets.token_hex(8)}_{filename}"
                    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads/identities')
                    
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                        
                    file.save(os.path.join(upload_folder, unique_filename))
                    identity_image_path = os.path.join(upload_folder, unique_filename)

            # 5. توليد المعرفات الفريدة (التعميد السيادي اللامركزي لعام 2026)
            # هنا يتم توليد المعرفات بشكل ديناميكي فريد لكل عملية إدخال ناجحة
            random_suffix = secrets.randbelow(900) + 100  # رقم عشوائي بين 100 و 999
            generated_sovereign_id = f"SUP-MAH{random_suffix}"
            generated_wallet_code = f"WEL-MAH{random_suffix}"

            # 6. حفظ البيانات في قاعدة البيانات الفعلية (مثال منطقي)
            # new_supplier = Supplier(username=username, sovereign_id=generated_sovereign_id, ...)
            # db.session.add(new_supplier)
            # db.session.commit()

            # 7. إرجاع استجابة الـ JSON الناجحة للنموذج لتشغيل الـ Modal
            return jsonify({
                "status": "success",
                "message": "تم إتمام التعميد والأرشفة السيادية بنجاح.",
                "data": {
                    "sovereign_id": generated_sovereign_id,
                    "wallet_code": generated_wallet_code
                }
            }), 200

        except Exception as e:
            # معالجة أي خطأ داخلي غير متوقع في السيرفر السحابي
            return jsonify({
                "status": "error",
                "message": f"فشل داخلي في السيرفر السحابي (500): {str(e)}"
            }), 500

    # في حالة طلب الصفحة عبر (GET)
    # نقوم بتمرير قاموس الـ endpoints فارغًا أو مهيأً لتفادي أي خطأ BuildError في قوالب Jinja2
    endpoints_config = {
        "add_supplier": url_for('admin_suppliers.add_supplier_page'),
        "check_duplicate": "/admin/suppliers/check-duplicate"
    }
    
    return render_template(
        'admin/add_supplier.html', 
        endpoints=endpoints_config,
        backup_csrf=secrets.token_hex(32)
    )


@admin_suppliers_bp.route('/admin/suppliers/check-duplicate', methods=['GET'])
def check_duplicate():
    """
    نقطة فحص التكرار اللحظية (API Endpoint) أثناء الكتابة في الواجهة الأمامية (Debounce Check).
    """
    check_type = request.args.get('type', '')
    value = request.args.get('value', '').strip()

    if not check_type or not value:
        return jsonify({"exists": False, "error": "المعاملات ناقصة"}), 400

    exists = False

    # فحص القيمة بناءً على نوع الحقل الممرر من الـ Dataset
    if check_type == 'username':
        exists = value in MOCK_DB["usernames"]
    elif check_type == 'identity_number':
        exists = value in MOCK_DB["identity_numbers"]
    elif check_type == 'owner_phone':
        exists = value in MOCK_DB["owner_phones"]
    elif check_type == 'trade_name':
        exists = value in MOCK_DB["trade_names"]
    elif check_type == 'bank_acc':
        exists = value in MOCK_DB["bank_accounts"]

    return jsonify({"exists": bool(exists)})
