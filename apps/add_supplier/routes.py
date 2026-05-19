# coding: utf-8
import os
import secrets
from flask import Blueprint, render_template, request, jsonify, current_app, url_for
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

# استيراد كائن قاعدة البيانات والـ Models وفقاً لبنية مشروعك المتوافقة مع مصنع التطبيقات
from apps import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import Wallet

# تعريف البلوبرنت الخاص بالموردين
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
            # استقبال البيانات الأساسية وتنظيفها من الفراغات
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

            # التحقق الخلفي الصارم (Server-side) من الحقول الإلزامية لسلامة النظام
            required_fields = [username, password, identity_type, identity_number, owner_name, trade_name, owner_phone, province, district, address_detail, bank_name, bank_acc]
            if not all(required_fields):
                return jsonify({"status": "error", "message": "⚠️ جميع الحقول الإلزامية يجب أن تكون مكتملة وصحيحة."}), 400

            # فحص ومنع تكرار البيانات الحيوية في قاعدة البيانات (PostgreSQL)
            if Supplier.query.filter_by(username=username).first():
                return jsonify({"status": "error", "message": "اسم المستخدم هذا محجوز مسبقاً."}), 400
            if Supplier.query.filter_by(identity_number=identity_number).first():
                return jsonify({"status": "error", "message": "رقم الوثيقة / الهوية مسجل مسبقاً."}), 400

            # معالجة رفع وثيقة الهوية وتخزينها في المسار المعتمد للمنصة
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

            # توليد الهويات السيادية الرقمية عبر الدالة الداخلية المعتمدة لديك في الموديل
            generated_sovereign_id = Supplier.generate_next_sovereign_id()
            
            if generated_sovereign_id.startswith("SUP-"):
                generated_wallet_code = generated_sovereign_id.replace("SUP-", "WEL-", 1)
            else:
                generated_wallet_code = f"WEL-{generated_sovereign_id}"

            # تشفير كلمة المرور لحماية الخصوصية والأمان السيادي للمنصة
            hashed_password = generate_password_hash(password)

            # تأسيس كائن المورد وتعميد البيانات
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
            
            # دفع البيانات إلى الجلسة مؤقتاً لتوليد المعرف الفرعي وتجنب قيود العلاقات (Foreign Key)
            db.session.flush()

            # تأسيس كائن المحفظة النقي والمستقر بالأرصدة التأسيسية المتعددة لـ (محجوب أونلاين)
            new_wallet = Wallet(
                wallet_code=generated_wallet_code,
                supplier_id=new_supplier.id,  # الربط المباشر مع المعرف الرقمي للمورد الراجع من الـ flush
                yer_total=0.0, yer_withdrawn=0.0, yer_pending=0.0,
                sar_total=0.0, sar_withdrawn=0.0, sar_pending=0.0,
                usd_total=0.0, usd_withdrawn=0.0, usd_pending=0.0,
                status="نشطة"
            )
            db.session.add(new_wallet)

            # التثبيت الشامل والنهائي لكافة العمليات المتسلسلة
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "تم الحفظ الفعلي وتعميد المحفظة بنجاح مطلق.",
                "redirect_url": url_for('admin_dashboard.list_suppliers'),  # التوجيه التلقائي الذكي لقائمة الموردين
                "data": {
                    "sovereign_id": generated_sovereign_id,
                    "wallet_code": generated_wallet_code
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"❌ خطأ تعميد المورد السحابي: {str(e)}")
            return jsonify({"status": "error", "message": f"فشل داخلي في السيرفر السحابي (500): {str(e)}"}), 500
        finally:
            db.session.close()  # 🔓 تحرير اتصال قاعدة البيانات فوراً لمنع أي تعليق أو تسريب للاتصالات

    # عند طلب الصفحة عبر GET، نمرر الإعدادات والمسارات لصفحة الـ HTML بشكل مرن ومتوافق مع الـ Factory
    endpoints_config = {
        "add_supplier": url_for('admin_suppliers.add_supplier_page'),
        "check_duplicate": url_for('admin_suppliers.check_duplicate')
    }
    return render_template('admin/add_supplier.html', endpoints=endpoints_config)


@admin_suppliers_bp.route('/admin/suppliers/check-duplicate', methods=['GET'])
def check_duplicate():
    """
    مسار فحص التكرار التفاعلي عبر الواجهة الأمامية وجلب التسلسل المتوقع القادم.
    """
    check_type = request.args.get('type', '')
    value = request.args.get('value', '').strip()

    # إذا كان الطلب قادماً لتحديث الهويات الافتراضية المتوقعة في أعلى الصفحة
    if check_type == 'get_next_sequence':
        try:
            next_seq = Supplier.generate_next_sovereign_id()
            return jsonify({'next_sequence': next_seq})
        except Exception:
            return jsonify({'next_sequence': 'SUP-MAH9631'})

    if not check_type or not value or check_type not in ['username', 'identity_number', 'owner_phone', 'trade_name', 'bank_acc']:
        return jsonify({"exists": False, "error": "المعاملات البرمجية غير مدعومة"}), 400

    try:
        exists = db.session.query(Supplier).filter(getattr(Supplier, check_type) == value).first() is not None
        return jsonify({"exists": bool(exists)})
    except Exception:
        return jsonify({"exists": False, "error": "فشل فحص قاعدة البيانات"})
    finally:
        db.session.close()  # 🔓 تحرير الاتصال فوراً لحفظ طاقة وكفاءة السيرفر
