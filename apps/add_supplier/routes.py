# coding: utf-8
# 🔑 محرك الموردين الحوكمي والسيادي - منصة محجوب أونلاين 2026

from flask import render_template, request, jsonify, current_app, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
import jinja2
import re  # مكتبة التعبيرات النمطية لمعالجة النصوص واستخراج الأرقام بدقة

# استيراد البلوبرينت المعزول الخاص بالموردين وكائن قاعدة البيانات
from . import admin_suppliers
from apps import db
from apps.models import Supplier  
from apps.models.wallet_db import Wallet  # استيراد موديل المحفظة الثلاثية الموحدة

def get_expected_sovereign_id():
    """
    سحب آخر معرف سيادي مسجل في قاعدة البيانات بدقة من خلال قراءة الجزء الرقمي 
    الأخير وزيادته بمقدار 1، ليعرض للمسؤول في الواجهة المعرف المتوقع تماماً.
    🛡️ تم تحصينه بطلب حقول مخصصة لمنع استدعاء الأعمدة المفقودة مؤقتاً أثناء الإقلاع.
    """
    default_prefix = "SUP-WEL-MAH"
    try:
        # جلب الحقول المحددة والأساسية فقط لقطع الطريق على استدعاء حقل status غير المتواجد
        last_supplier = db.session.query(Supplier.id, Supplier.sovereign_id)\
                                  .order_by(Supplier.id.desc())\
                                  .first()
        
        if last_supplier and last_supplier.sovereign_id:
            sovereign_str = last_supplier.sovereign_id.strip()
            
            # استخراج كافة الأرقام المتتالية في نهاية المعرف السيادي
            match = re.search(r'\d+$', sovereign_str)
            if match:
                last_num = int(match.group())
                next_num = last_num + 1
                
                # استخراج البادئة النصية الديناميكية التي تسبق الرقم مباشرة (مثل SUP-WEL-MAH)
                prefix_match = re.match(r'^(.*?)(\d+)$', sovereign_str)
                if prefix_match:
                    return f"{prefix_match.group(1)}{next_num}"
                
                return f"{default_prefix}{next_num}"
        
        # ملاذ آمن: في حال وجود سجلات لا تطابق النمط المعتاد في النظام
        if last_supplier:
            return f"{default_prefix}96319"

    except Exception as e:
        current_app.logger.error(f"❌ خطأ أثناء احتساب المعرف السيادي القادم: {str(e)}")
    
    # في حال كان الجدول فارغاً تماماً في البداية
    return f"{default_prefix}96319"


@admin_suppliers.route('/add', methods=['GET', 'POST'], endpoint='add_supplier_page')
@admin_suppliers.route('/add_legacy', methods=['GET', 'POST'], endpoint='add_supplier')
@login_required
def add_supplier_page():
    if request.method == 'POST':
        try:
            # 1. استقبال البيانات السبعة والبيانات المساعدة من الواجهة وعمل تطهير (strip) فوري
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

            # ==================== التحديث السيادي الجديد لعام 2026 ====================
            # استقبال الرتبة والمستوى التشغيلي من الواجهة (ريادي، سيادي، ملكي)
            user_rank = request.form.get('user_rank', 'ريادي').strip()
            # حقن التفعيل التلقائي الفوري للحساب بمجرد الاعتماد والضغط من الإدارة العليا
            system_status = 'active'
            # =========================================================================

            # التحقق الفوري الحوكمي من عدم إرسال حقول أساسية فارغة
            required_post_fields = {
                "username": username, "identity_number": identity_number, 
                "owner_name": owner_name, "trade_name": trade_name, 
                "owner_phone": owner_phone, "shop_phone": shop_phone, "bank_acc": bank_acc
            }
            for f_key, f_val in required_post_fields.items():
                if not f_val:
                    return jsonify({
                        "status": "error",
                        "message": f"تنبيه سيادي: لا يمكن تعميد المورد والحقل الأساسي ({f_key}) فارغ."
                    }), 400

            # 2. فحص الحقول السبعة بشكل صارم في الخلفية قبل إتمام الحفظ لمنع تجاوز التكرار
            # 🛡️ تم تعديل الفحص للاستعلام عن الـ ID فقط لضمان عدم حدوث تعارض مع أعمدة مفقودة
            check_fields = {
                "username": (db.session.query(Supplier.id).filter_by(username=username).first(), "اسم المستخدم (Login)"),
                "identity_number": (db.session.query(Supplier.id).filter_by(identity_number=identity_number).first(), "رقم الوثيقة / الهوية"),
                "owner_name": (db.session.query(Supplier.id).filter_by(owner_name=owner_name).first(), "اسم المالك الكامل"),
                "trade_name": (db.session.query(Supplier.id).filter_by(trade_name=trade_name).first(), "الاسم التجاري للمنشأة"),
                "owner_phone": (db.session.query(Supplier.id).filter_by(owner_phone=owner_phone).first(), "رقم هاتف المالك"),
                "shop_phone": (db.session.query(Supplier.id).filter_by(shop_phone=shop_phone).first(), "هاتف المنشأة (محل)"),
                "bank_acc": (db.session.query(Supplier.id).filter_by(bank_acc=bank_acc).first(), "رقم الحساب")
            }

            for key, (exists, field_title) in check_fields.items():
                if exists:
                    return jsonify({
                        "status": "error",
                        "message": f"تنبيه حوكمي: حقل ({field_title}) مسجل مسبقاً في النظام ومحفوظ، يرجى تعديله."
                    }), 400

            # 3. تشفير كلمة المرور وبناء الكائن السيادي المحدث
            hashed_password = generate_password_hash(password)
            
            new_supplier = Supplier(
                username=username,
                password_hash=hashed_password,
                identity_type=identity_type,
                identity_number=identity_number,
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
                registration_source='لوحة التحكم',
                rank_grade=user_rank,         # حفظ الرتبة الفخمة المختارة
                status=system_status,         # تفعيل فوري ومطلق في حقل النظام الأساسي
                created_by_id=current_user.id if hasattr(current_user, 'id') else None
            )

            # 4. تعميد وإدراج المورد في قاعدة البيانات مؤقتاً لسحب المعرف الفريد
            db.session.add(new_supplier)
            db.session.flush()  # سحب الـ ID المولد تلقائياً للمورد الجديد دون إنهاء الجلسة

            # 5. 💳 الحقن المالي التلقائي: إنشاء محفظة موحدة بثلاث عملات وربطها بالـ supplier_id فوراً
            supplier_wallet = Wallet(
                supplier_id=new_supplier.id,  # ربط المحفظة بالـ ID الفريد للمورد المولد أعلاه
                # عملة الريال اليمني
                yer_total=0.0,
                yer_available=0.0,
                yer_pending=0.0,
                yer_withdrawn=0.0,
                # عملة الريال السعودي
                sar_total=0.0,
                sar_available=0.0,
                sar_pending=0.0,
                sar_withdrawn=0.0,
                # عملة الدولار الأمريكي
                usd_total=0.0,
                usd_available=0.0,
                usd_pending=0.0,
                usd_withdrawn=0.0
            )
            db.session.add(supplier_wallet)

            # 6. حفظ العملية التبادلية كاملة لضمان التزامن المالي الهيكلي المستقر
            db.session.commit()

            # دمج مخرجات دالة الـ Property لقراءة الـ state_title اللفظية وإرسالها للمودال
            return jsonify({
                "status": "success",
                "message": "تم تعميد المورد وتنشيطه بنجاح وتوليد محفظته المالية الثلاثية تلقائياً في النظام الحوكمي السيادي.",
                "data": {
                    "username": new_supplier.username,
                    "sovereign_id": new_supplier.sovereign_id,
                    "rank_grade": new_supplier.rank_grade,
                    "state_title": new_supplier.state_title
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"❌ خطأ بنيوي أثناء حفظ المورد: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"حدث خطأ غير متوقع في قاعدة البيانات: {str(e)}"
            }), 500

    # مرحلة الـ GET لعرض واجهة الإدخال للمسؤول
    sovereign_id = get_expected_sovereign_id()
    
    csrf_val = ""
    try:
        if 'csrf' in current_app.extensions:
            from flask_wtf.csrf import generate_csrf
            csrf_val = generate_csrf()
    except Exception:
        pass

    try:
        return render_template('admin/add_supplier.html', sovereign_id=sovereign_id, owner=current_user, backup_csrf=csrf_val)
    except jinja2.exceptions.TemplateNotFound:
        return render_template('add_supplier.html', sovereign_id=sovereign_id, owner=current_user, backup_csrf=csrf_val)


@admin_suppliers.route('/check-duplicate', methods=['GET'])
@login_required
def check_duplicate():
    """
    مستمع الفحص الفوري واللحظي المباشر لقاعدة البيانات لضمان الحوكمة وسرعة الاستجابة.
    تم تطوير الاستجابة لتعود بـ 'exists': true في حال التكرار أو الفراغ الخادع لمنع علامات الصح.
    🛡️ تم تحصينه بطلب حقل الـ ID فقط لضمان الفحص اللحظي الآمن دون استدعاء الحقول المتغيرة.
    """
    check_type = request.args.get('type')
    value = request.args.get('value', '').strip()
    
    # حوكمة صارمة: إذا أرسلت الواجهة قيمة فارغة أو مسافات فقط، نعتبرها مكررة/مرفوضة فوراً لقطع علامة الصح
    if not check_type or not value:
        return jsonify({"exists": True, "error": "المدخلات فارغة أو غير سليمة"}), 200
        
    is_duplicate = False
    try:
        # ربط دقيق وشامل للحقول السبعة بمسميات الواجهة لمنع التكرار البنيوي عبر الـ ID حصراً
        if check_type == 'username':
            is_duplicate = db.session.query(Supplier.id).filter_by(username=value).first() is not None
            
        elif check_type == 'identity_number':
            is_duplicate = db.session.query(Supplier.id).filter_by(identity_number=value).first() is not None
            
        elif check_type == 'owner_name':
            is_duplicate = db.session.query(Supplier.id).filter_by(owner_name=value).first() is not None
            
        elif check_type == 'trade_name':
            is_duplicate = db.session.query(Supplier.id).filter_by(trade_name=value).first() is not None
            
        elif check_type == 'owner_phone':
            is_duplicate = db.session.query(Supplier.id).filter_by(owner_phone=value).first() is not None
            
        elif check_type == 'shop_phone':
            is_duplicate = db.session.query(Supplier.id).filter_by(shop_phone=value).first() is not None
            
        elif check_type == 'bank_acc':
            is_duplicate = db.session.query(Supplier.id).filter_by(bank_acc=value).first() is not None
            
        else:
            current_app.logger.warning(f"⚠️ نوع فحص غير مدعوم في منصة محجوب: {check_type}")

    except Exception as e:
        current_app.logger.error(f"❌ خطأ أثناء الاستعلام اللحظي للحقل [{check_type}]: {str(e)}")
        return jsonify({"exists": True, "error": "Database error"}), 500
        
    return jsonify({"exists": is_duplicate})
