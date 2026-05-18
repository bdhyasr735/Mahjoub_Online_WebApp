import os
import secrets
from flask import Blueprint, render_template, request, jsonify, current_app, url_for
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

from apps import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import Wallet

admin_suppliers_bp = Blueprint(
    'admin_suppliers', 
    __name__, 
    template_folder='templates',
    static_folder='static'
)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ─── المسارات (Routes) ───

@admin_suppliers_bp.route('/admin/suppliers/add', methods=['GET', 'POST'])
def add_supplier_page():
    """
    عرض صفحة تعميد المورد والمعالجة السحابية الفورية والسريعة بدون تعليق.
    """
    if request.method == 'POST':
        try:
            # استقبال البيانات الأساسية وتنظيفها
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

            # التحقق الخلفي من الحقول الإلزامية
            if not all([username, password, identity_type, identity_number, owner_name, trade_name, owner_phone, province, district, address_detail, bank_name, bank_acc]):
                return jsonify({"status": "error", "message": "⚠️ جميع الحقول الإلزامية يجب أن تكون مكتملة وصحيحة."}), 400

            # فحص ومنع تكرار البيانات الحيوية
            if Supplier.query.filter_by(username=username).first():
                return jsonify({"status": "error", "message": "اسم المستخدم هذا محجوز مسبقاً."}), 400
            if Supplier.query.filter_by(identity_number=identity_number).first():
                return jsonify({"status": "error", "message": "رقم الوثيقة / الهوية مسجل مسبقاً."}), 400

            # معالجة رفع الملفات
            identity_image_db_path = None
            if 'identity_image' in request.files:
                file = request.files['identity_image']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = f"doc_{secrets.token_hex(8)}_{filename}"
                    base_upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'identities')
                    os.makedirs(base_upload_folder, exist_ok=True)
                    file.save(os.path.join(base_upload_folder, unique_filename))
                    identity_image_db_path = f"uploads/identities/{unique_filename}"

            # توليد الهويات السيادية الرقمية
            generated_sovereign_id = Supplier.generate_next_sovereign_id()
            
            if generated_sovereign_id.startswith("SUP-"):
                generated_wallet_code = generated_sovereign_id.replace("SUP-", "WEL-", 1)
            else:
                generated_wallet_code = f"WEL-{generated_sovereign_id}"

            hashed_password = generate_password_hash(password)

            # تأسيس كائن المورد
            new_supplier = Supplier(
                username=username,
                password_hash=hashed_password,  
                sovereign_id=generated_sovereign_id,
                wallet_code=generated_wallet_code,
                identity_type=identity_type,
                identity_number=identity_number,
                identity_image=identity_image_db_path,
                owner_name=owner_name,
                trade_name=trade_name,
                owner_phone=owner_phone,
                shop_phone=shop_phone,
                province=province,
                district=district,
                address_detail=address_detail,
                fin_type=fin_type,
                bank_name=bank_name,
                bank_acc=bank_acc,
                activity_type=activity_type,
                status="نشط"
            )
            db.session.add(new_supplier)
            
            # حجز الهوية في الجلسة أولاً لتفادي قيود المفاتيح الأجنبية
            db.session.flush()

            # تأسيس كائن المحفظة النقي والمستقر بالأرصدة التأسيسية
            new_wallet = Wallet(
                wallet_code=generated_wallet_code,
                supplier_id=generated_sovereign_id,
                yer_total=0.0, yer_withdrawn=0.0, yer_pending=0.0,
                sar_total=0.0, sar_withdrawn=0.0, sar_pending=0.0,
                usd_total=0.0, usd_withdrawn=0.0, usd_pending=0.0,
                status="نشطة"
            )
            db.session.add(new_wallet)

            # التثبيت النهائي الشامل
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "تم الحفظ الفعلي وتعميد المحفظة بنجاح مطلق.",
                "data": {
                    "sovereign_id": generated_sovereign_id,
                    "wallet_code": generated_wallet_code
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": f"فشل داخلي في السيرفر السحابي (500): {str(e)}"}), 500
        finally:
            db.session.close()  # 🔓 تحرير الاتصال فوراً لمنع أي تعليق مستقبلي

    endpoints_config = {
        "add_supplier": url_for('admin_suppliers.add_supplier_page'),
        "check_duplicate": url_for('admin_suppliers.check_duplicate')
    }
    return render_template('admin/add_supplier.html', endpoints=endpoints_config)


@admin_suppliers_bp.route('/admin/suppliers/check-duplicate', methods=['GET'])
def check_duplicate():
    check_type = request.args.get('type', '')
    value = request.args.get('value', '').strip()

    if not check_type or not value or check_type not in ['username', 'identity_number', 'owner_phone', 'trade_name', 'bank_acc']:
        return jsonify({"exists": False, "error": "المعاملات البرمجية غير مدعومة"}), 400

    try:
        exists = db.session.query(Supplier).filter(getattr(Supplier, check_type) == value).first() is not None
        return jsonify({"exists": bool(exists)})
    except Exception:
        return jsonify({"exists": False, "error": "فشل فحص قاعدة البيانات"})
    finally:
        db.session.close()  # 🔓 تحرير الاتصال فوراً
