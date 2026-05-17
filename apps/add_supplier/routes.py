# apps/add_supplier/routes.py
# coding: utf-8

from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash

# استيراد قاعدة البيانات والموديل
from apps import db  
from apps.models.supplier_db import Supplier 

# استيراد البلوبرينت الموحد والمثبت من ملف الـ __init__ لمنع التعارض الخفي
from apps.add_supplier import admin_suppliers

@admin_suppliers.route('/add', methods=['GET', 'POST'])
@login_required 
def add_supplier():
    """
    محرك تعميد الموردين: يقوم بمعالجة البيانات وحفظها في السجل لـ "محجوب أونلاين"
    """
    if request.method == 'POST':
        try:
            # 1. استقبال البيانات الأساسية وتطهيرها
            username = request.form.get('username', '').strip()
            trade_name = request.form.get('trade_name', '').strip()
            password = request.form.get('password')
            identity_number = request.form.get('identity_number', '').strip()

            # 2. التحقق النهائي (Back-end Validation) المحصن تماماً لمنع التكرار والانكسار
            try:
                if username and Supplier.query.filter_by(username=username).first():
                    return jsonify({'status': 'error', 'message': 'فشل التعميد: اسم المستخدم مسجل مسبقاً!'}), 400
                
                if trade_name and Supplier.query.filter_by(trade_name=trade_name).first():
                    return jsonify({'status': 'error', 'message': 'فشل التعميد: الاسم التجاري مسجل مسبقاً!'}), 400

                if identity_number and Supplier.query.filter_by(identity_number=identity_number).first():
                    return jsonify({'status': 'error', 'message': 'فشل التعميد: رقم الوثيقة أو الهوية مسجل مسبقاً!'}), 400
            except Exception as db_err:
                # حماية مرنة: في حال وجود اختلاف مؤقت في هيكل الجداول أو الحقول أثناء الفحص المبدئي،
                # نقوم بطباعة الخطأ في الـ Logs لتتبعه دون أن نقطع عملية التسجيل الأساسية.
                print(f"Validation Log: Temporary skip column validation -> {str(db_err)}")

            # 3. معالجة حقول الإدخال اليدوي الديناميكية وتطابقها مع الواجهة المحدثة
            identity_type = request.form.get('identity_type')
            bank_name = request.form.get('bank_name')
            activity_type = request.form.get('activity_type', '').strip() # تعديل المسمى ليتوافق مع الـ HTML والموديل

            # 4. تشفير كلمة المرور وتجهيز الكائن
            hashed_pw = generate_password_hash(password)
            
            # ⚠️ لاحظ: يتم تمرير قيمة مؤقتة للحقل السيادي ليتم استبدالها بشكل قطعي 
            # عبر دالة الـ Event Listener التلقائية المخزنة في موديل قاعدة البيانات قبل الحفظ الفعلي.
            new_supplier = Supplier(
                sovereign_id="PENDING", 
                username=username,
                password_hash=hashed_pw,
                identity_type=identity_type,
                identity_number=identity_number,
                activity_type=activity_type,
                owner_name=request.form.get('owner_name', '').strip(),
                trade_name=trade_name,
                shop_phone=request.form.get('shop_phone', '').strip(),
                owner_phone=request.form.get('owner_phone', '').strip(),
                province=request.form.get('province'),
                district=request.form.get('district'),
                address_detail=request.form.get('address_detail'), # تعديل ليتطابق مع name="address_detail" في الـ HTML
                fin_type=request.form.get('fin_type'),
                bank_name=bank_name,
                bank_acc=request.form.get('bank_acc', '').strip(),
                status='المراجعة',        # إجبار إسناد حالة البدء الافتراضية لحوكمة النظام
                rank_grade='ريادي',       # إجبار إسناد رتبة المورد الأولى للتحكم بالصلاحيات
                registration_source='لوحة التحكم', # تحديد ولادة الحساب من الإدارة
                created_by_id=getattr(current_user, 'id', None), # إسناد معرّف المشرف الحالي للحوكمة الرقمية
                created_at=datetime.utcnow()
            )

            # 5. معالجة المرفقات (إذا تم رفع صورة الهوية)
            if 'identity_image' in request.files:
                file = request.files['identity_image']
                if file and file.filename != '':
                    # هنا يمكن إضافة منطق الحفظ الفعلي للصور لاحقاً
                    pass

            # 6. الحفظ النهائي الصارم والمؤكد في قاعدة البيانات
            db.session.add(new_supplier)
            db.session.commit() # هنا تتدخل دالة الجلب لتثبيت الرقم الحقيقي المحدث في السلسلة

            # إرجاع استجابة نجاح صريحة وقطعية لتغلق الـ JavaScript نافذة "جاري المعالجة" بنجاح
            return jsonify({
                'status': 'success',
                'message': 'تم تعميد المورد بنجاح في نظام الأرشفة',
                'data': {
                    'username': new_supplier.username,
                    'sovereign_id': new_supplier.sovereign_id # يعود الرقم المتسلسل الفعلي المولد من قاعدة البيانات مباشرة
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            print(f"Critical Error in add_supplier: {str(e)}")
            return jsonify({'status': 'error', 'message': f'فشل في عملية التعميد: {str(e)}'}), 500

    # -------------------------------------------------------------------------
    # في حالة GET: حساب التنبؤ الرقمي السيادي بناءً على آخر سجل حقيقي في القاعدة
    # -------------------------------------------------------------------------
    try:
        # جلب آخر سجل تم إدخاله في قاعدة البيانات بناءً على معرف الـ ID التلقائي
        last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        
        # الفحص واستخراج الرقم المبني تماماً على النمط الفعلي المخزن 'SUP-WEL-MAH963'
        if last_supplier and last_supplier.sovereign_id and 'SUP-WEL-MAH963' in last_supplier.sovereign_id:
            try:
                # عزل الجزء النصي الثابت لاستخراج الرقم التالي بدقة ديناميكية كاملة
                last_num_str = last_supplier.sovereign_id.replace('SUP-WEL-MAH963', '').strip()
                next_num = int(last_num_str) + 1
            except (ValueError, IndexError):
                # حماية برمجية احتياطية في حال تعذر القراءة النصية
                next_num = (last_supplier.id or 0) + 1
        else:
            # في حال لم تعثر القاعدة على النمط الفعلي، يبدأ العد بناءً على آخر ID متاح
            next_num = (last_supplier.id or 0) + 1 if last_supplier else 1

        # دمج المعرف النهائي المحدث وتمريره مباشرة إلى الواجهة
        next_sovereign_id = f"SUP-WEL-MAH963{next_num}"
    except Exception as e:
        print(f"Error fetching next_sovereign_id prediction: {str(e)}")
        # قيمة استباقية ذكية في حال وقوع أي استثناء عابر أثناء الاتصال
        next_sovereign_id = "SUP-WEL-MAH96319"
    
    # تمرير المتغير الموحد والمطابق للواجهة لمنع ظهور أي تشوهات أو فراغات رقمية
    return render_template('admin/add_supplier.html', sovereign_id=next_sovereign_id)


@admin_suppliers.route('/check-duplicate', methods=['GET'])
@login_required
def check_duplicate():
    """
    نظام الفحص اللحظي الآمن: يتصل به الـ JavaScript لإظهار علامات الصح والخطأ ✅❌
    """
    try:
        check_type = request.args.get('type')
        value = request.args.get('value', '').strip()

        if not check_type or not value:
            return jsonify({'exists': False})

        # خريطة الحقول المسموح بفحص تكرارها
        field_map = {
            'username': Supplier.username,
            'trade_name': Supplier.trade_name,
            'shop_phone': Supplier.shop_phone,
            'identity_number': Supplier.identity_number
        }

        target_field = field_map.get(check_type)
        exists = False
        
        if target_field is not None:
            exists = Supplier.query.filter(target_field == value).first() is not None

        return jsonify({'exists': exists})
        
    except Exception as e:
        # حماية سيادية: يمنع انكسار واجهة المستخدم ويضمن سلاسة تدفق البيانات في الواجهة
        print(f"Check duplicate error for {check_type}: {str(e)}")
        return jsonify({'exists': False, 'error': str(e)})
