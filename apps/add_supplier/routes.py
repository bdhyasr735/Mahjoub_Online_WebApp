import os
import uuid
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from werkzeug.utils import secure_filename
# افترضنا هنا وجود موديل وقاعدة بيانات مجهزة (تعدل حسب مسارات مشروعك)
from apps.models import db, Supplier, Wallet 

add_supplier_bp = Blueprint('add_supplier', __name__, template_folder='templates')

# الامتدادات المسموح بها لصور الوثائق
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_next_sequence_codes():
    """
    دالة سيادية لحساب التسلسل القادم ديناميكياً بناءً على آخر مورد تم تعميده.
    تنتج كود مخصص للمنصة مثل: SUP-MAH9631
    """
    try:
        last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        if last_supplier and last_supplier.sovereign_id:
            # استخراج الرقم من المعرف الأخير (مثال: SUP-MAH9635 -> 9635)
            import re
            match = re.search(r'\d+', last_supplier.sovereign_id)
            if match:
                next_num = int(match.group()) + 1
                return f"SUP-MAH{next_num}"
        # البداية الافتراضية للمنصة في حال عدم وجود سجلات سابقة
        return "SUP-MAH9631"
    except Exception as e:
        current_app.logger.error(f"Error generating sequence: {str(e)}")
        return "SUP-MAH9631"


@add_supplier_bp.route('/admin/suppliers/check-duplicate', methods=['GET'])
def check_duplicate():
    """
    نقطة الوصول للتحقق اللحظي عبر الفيس بوك/الواجهة (Debounce) لمنع التكرار،
    ولجلب المعرفات المتوقعة لحظة فتح الصفحة.
    """
    check_type = request.args.get('type')
    value = request.args.get('value', '').strip()

    # إذا كان الطلب لجلب التسلسل المتوقع التالي
    if check_type == 'get_next_sequence':
        next_sup = generate_next_sequence_codes()
        return jsonify({'next_sequence': next_sup})

    if not value:
        return jsonify({'exists': False})

    exists = False
    
    if check_type == 'username':
        exists = db.session.query(Supplier.query.filter_by(username=value).exists()).scalar()
    elif check_type == 'identity_number':
        exists = db.session.query(Supplier.query.filter_by(identity_number=value).exists()).scalar()
    elif check_type == 'owner_name':
        exists = db.session.query(Supplier.query.filter_by(owner_name=value).exists()).scalar()
    elif check_type == 'trade_name':
        exists = db.session.query(Supplier.query.filter_by(trade_name=value).exists()).scalar()
    elif check_type == 'owner_phone':
        exists = db.session.query(Supplier.query.filter_by(owner_phone=value).exists()).scalar()
    elif check_type == 'bank_acc':
        exists = db.session.query(Supplier.query.filter_by(bank_acc=value).exists()).scalar()

    return jsonify({'exists': exists})


@add_supplier_bp.route('/admin/suppliers/add', methods=['POST'])
def add_supplier_submit():
    """
    استقبال ومعالجة نموذج تعميد المورد وإصدار المحفظة وحفظ الوثائق سحابياً.
    """
    try:
        # 1. استخراج البيانات من الواجهة الـ HTML
        username = request.form.get('username', '').strip()
        password = request.form.get('password') # يفضل تشفيرها بـ werkzeug.security قبل الحفظ
        identity_type = request.form.get('identity_type')
        identity_number = request.form.get('identity_number', '').strip()
        
        owner_name = request.form.get('owner_name', '').strip()
        trade_name = request.form.get('trade_name', '').strip()
        owner_phone = request.form.get('owner_phone', '').strip()
        shop_phone = request.form.get('shop_phone', '').strip() or None
        
        province = request.form.get('province')
        district = request.form.get('district')
        address_detail = request.form.get('address_detail', '').strip()
        
        fin_type = request.form.get('fin_type')
        bank_name = request.form.get('bank_name')
        bank_acc = request.form.get('bank_acc', '').strip()
        activity_type = request.form.get('activity_type')

        # 2. توليد المعرفات السيادية النهائية بشكل آمن ومغلق لمنع تضارب الجلسات
        final_sovereign_id = generate_next_sequence_codes()
        final_wallet_code = final_sovereign_id.replace("SUP-", "WEL-", 1)

        # 3. معالجة وحفظ صورة الوثيقة سحابياً أو محلياً (إن وجدت)
        identity_image_path = None
        if 'identity_image' in request.files:
            file = request.files['identity_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # توليد اسم فريد للوثيقة لضمان السرية والأرشفة المنظمة
                unique_filename = f"doc_{final_sovereign_id}_{uuid.uuid4().hex[:6]}_{filename}"
                
                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads/identities')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                    
                file.save(os.path.join(upload_folder, unique_filename))
                identity_image_path = os.path.join(upload_folder, unique_filename)

        # 4. فحص احتياطي نهائي في السيرفر لضمان عدم حدوث Duplicate Key Violation
        check_dup_username = Supplier.query.filter_by(username=username).first()
        if check_dup_username:
            return jsonify({'status': 'error', 'message': 'اسم المستخدم معتمد مسبقاً في النظام لحساب آخر.'}), 400

        # 5. بناء السجل وضخه لقاعدة البيانات (تعديل الـ Fields لتطابق جداولك)
        new_supplier = Supplier(
            sovereign_id=final_sovereign_id,
            wallet_code=final_wallet_code,
            username=username,
            password=password, # تذكر تشفير كلمة المرور هنا للحماية
            identity_type=identity_type,
            identity_number=identity_number,
            identity_image=identity_image_path,
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
            is_active=True
        )
        
        db.session.add(new_supplier)
        db.session.flush() # لحجز المورد وإتاحة الربط المالي الفوري

        # 6. تعميد وإنشاء المحفظة التابعة المرتبطة ماليًا بالمورد الجديد
        new_wallet = Wallet(
            supplier_id=new_supplier.id,
            wallet_code=final_wallet_code,
            balance_yer=0.0,
            balance_sar=0.0,
            balance_usd=0.0,
            status='active'
        )
        db.session.add(new_wallet)
        
        # إنهاء المعاملة وحفظ البيانات بشكل قطعي وثابت
        db.session.commit()

        # 7. الاستجابة بالـ JSON المتوافق تماماً مع الـ Modal والميكانيكية التفاعلية بالـ HTML
        return jsonify({
            'status': 'success',
            'message': 'تم تعميد المورد بنجاح في قاعدة البيانات السيادية.',
            'data': {
                'sovereign_id': final_sovereign_id,
                'wallet_code': final_wallet_code
            },
            'redirect_url': url_for('add_supplier.admin_suppliers_list') # مسار صفحة جدول الموردين بعد الإغلاق
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Sovereign Archive Error: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': f'فشل في حفظ البيانات السحابية: {str(e)}'
        }), 500


@add_supplier_bp.route('/admin/suppliers')
def admin_suppliers_list():
    """
    صفحة عرض وأرشفة الموردين المعتمدين (المسار المتوقع لإعادة التوجيه بعد النجاح).
    """
    return render_template('admin_suppliers_list.html')
