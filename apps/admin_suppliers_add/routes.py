# coding: utf-8
# 📂 apps/admin_suppliers_add/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from flask_login import login_required
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.wallet_db import SupplierWallet
from sqlalchemy.exc import IntegrityError
import secrets
import re

admin_suppliers_add_bp = Blueprint(
    'admin_suppliers_add_bp', 
    __name__, 
    template_folder='templates'
)

# -----------------------------------------------------------
# API: للتحقق اللحظي والحي في الخلفية (فحص التكرار عبر الـ AJAX)
# -----------------------------------------------------------
@admin_suppliers_add_bp.route('/check_availability', methods=['POST'])
@login_required
def check_availability():
    """توفير فحص ديناميكي فوري لمنع تكرار البيانات قبل اعتماد الإرسال من الواجهات."""
    data = request.get_json() or {}
    field_type = data.get('type')  # 'username' أو 'phone'
    value = data.get('value', '').strip()

    if not value:
        return jsonify({'available': False, 'message': '⚠️ الحقل فارغ'})

    # 1. التحقق من توفر اسم المستخدم في جداول الموردين والموظفين معاً لمنع تداخل الجلسات
    if field_type == 'username':
        owner_exists = Supplier.query.filter_by(username=value).first()
        staff_exists = SupplierStaff.query.filter_by(username=value).first()
        
        if owner_exists or staff_exists:
            return jsonify({'available': False, 'message': 'اسم المستخدم مسجل مسبقاً في النظام'})
        return jsonify({'available': True, 'message': 'اسم المستخدم متاح للاستخدام'})

    # 2. التحقق من توفر وصحة رقم الهاتف (9 أرقام محلية بدون مفتاح دولي)
    elif field_type == 'phone':
        if not re.match(r'^\d{9}$', value):
            return jsonify({'available': False, 'message': 'يجب أن يتكون رقم الهاتف من 9 أرقام فقط'})
            
        owner_exists = Supplier.query.filter_by(phone=value).first()
        staff_exists = SupplierStaff.query.filter_by(phone=value).first()
        
        if owner_exists or staff_exists:
            return jsonify({'available': False, 'message': 'رقم الهاتف مرتبط بحساب آخر مسبقاً'})
        return jsonify({'available': True, 'message': 'رقم الهاتف متاح للاستخدام'})

    return jsonify({'available': False, 'message': '⚠️ نوع الفحص غير مدعوم'})


# -----------------------------------------------------------
# مسار الحفظ والمعالجة الرئيسي لبيانات النماذج (GET & POST)
# -----------------------------------------------------------
@admin_suppliers_add_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier_or_staff():
    """نقطة دخول موحدة وآمنة لإضافة مورد (مالك كيان) أو موظف تشغيلي مع أتمتة المحفظة المالية."""
    
    if request.method == 'POST':
        action_type = request.form.get('action_type')  # 'owner' أو 'staff'
        temp_password = secrets.token_hex(4)  # توليد كلمة مرور عشوائية آمنة وصارمة (8 خانات)
        
        try:
            # ================= أولاً: معالجة إضافة المورد المالك =================
            if action_type == 'owner':
                username = request.form.get('username', '').strip()
                phone = request.form.get('phone', '').strip()
                trade_name = request.form.get('trade_name', '').strip()
                rank = request.form.get('rank', 'bronze')

                # جدار حماية خلفي لبيانات الهاتف لضمان سلامة البيانات قبل التخزين
                if not re.match(r'^\d{9}$', phone):
                    flash("❌ خطأ: رقم هاتف المورد يجب أن يتكون من 9 أرقام فقط.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                # التحقق الأمني الخلفي الصارم من التكرار لحظر أي تلاعب في الـ HTML من المتصفح
                if Supplier.query.filter_by(username=username).first() or SupplierStaff.query.filter_by(username=username).first():
                    flash("❌ خطأ: اسم المستخدم مسجل مسبقاً لمورد أو موظف آخر.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                if Supplier.query.filter_by(phone=phone).first() or SupplierStaff.query.filter_by(phone=phone).first():
                    flash("❌ خطأ: رقم الهاتف مسجل مسبقاً في النظام.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                # 1. إنشاء كيان المورد الجديد بنجاح
                new_supplier = Supplier(
                    username=username,
                    trade_name=trade_name,
                    rank=rank,
                    status='active'
                )
                new_supplier.phone = phone 
                new_supplier.set_password(temp_password)
                
                db.session.add(new_supplier)
                db.session.commit()  # حفظ الكيان لتوليد الـ ID الفريد تلقائياً من السيرفر
                
                # 2. أتمتة إنشاء المحفظة المالية المرتبطة بالمورد المحدث مباشرة
                wallet_code = f"MAH-WEL{new_supplier.id}"
                new_wallet = SupplierWallet(
                    wallet_code=wallet_code,
                    supplier_id=new_supplier.id
                )
                db.session.add(new_wallet)
                db.session.commit()
                
                # 🌟 تخزين بيانات الحساب الجديد في الجلسة ليتم التقاطها وعرضها في المودال بعد الـ Redirect
                session['new_user_data'] = {
                    'type': '🏬 مورد جديد (مالك كيان تجاري)',
                    'trade_name': new_supplier.trade_name,
                    'username': new_supplier.username,
                    'password': temp_password
                }
                
                flash(f"✅ تم تسجيل المورد بنجاح وإنشاء محفظته المالية: {new_supplier.trade_name}", "success")
                
            # ================= ثانياً: معالجة إضافة الموظف التشغيلي =================
            elif action_type == 'staff':
                staff_username = request.form.get('staff_username', '').strip()
                staff_phone = request.form.get('staff_phone', '').strip()
                supplier_id = request.form.get('supplier_id')

                # التحقق من اختيار المورد
                if not supplier_id:
                    flash("❌ خطأ: يجب اختيار المورد القانوني الذي يتبع له الموظف.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                # جدار حماية خلفي لبيانات هاتف الموظف
                if not re.match(r'^\d{9}$', staff_phone):
                    flash("❌ خطأ: رقم هاتف الموظف يجب أن يتكون من 9 أرقام فقط.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                # فحص منع التكرار الخلفي للموظف
                if Supplier.query.filter_by(username=staff_username).first() or SupplierStaff.query.filter_by(username=staff_username).first():
                    flash("❌ خطأ: اسم مستخدم الموظف مسجل مسبقاً بالحسابات المعتمدة.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                if Supplier.query.filter_by(phone=staff_phone).first() or SupplierStaff.query.filter_by(phone=staff_phone).first():
                    flash("❌ خطأ: رقم هاتف الموظف مسجل مسبقاً في النظام.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                # 3. إنشاء كائن الموظف التابع وتحديد رتبته التشغيلية
                new_staff = SupplierStaff(
                    supplier_id=supplier_id,
                    username=staff_username,
                    phone=staff_phone,
                    role='worker'
                )
                new_staff.set_password(temp_password)
                
                db.session.add(new_staff)
                db.session.commit()
                
                # جلب اسم المورد الرئيسي التابع له لعرضه بشكل منسق في وثيقة النجاح المنسوخة
                parent_supplier = Supplier.query.get(supplier_id)
                parent_name = parent_supplier.trade_name if parent_supplier else "غير محدد"

                # 🌟 تخزين بيانات الموظف الجديد في الجلسة لإرسالها فوراً إلى نافذة المودال التفاعلية
                session['new_user_data'] = {
                    'type': '🔑 موظف تشغيلي (تابع لمورد)',
                    'trade_name': parent_name,
                    'username': new_staff.username,
                    'password': temp_password
                }
                
                flash(f"✅ تم إضافة الموظف بنجاح وتعيينه للعمل: {new_staff.username}", "success")
            
            return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

        except IntegrityError:
            db.session.rollback()
            flash("❌ خطأ فني: البيانات المدخلة تسببت في تعارض مع قواعد البيانات (مكررة).", "danger")
            return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))
        except Exception as e:
            db.session.rollback()
            flash(f"⚠️ حدث خطأ تقني غير متوقع: {str(e)}", "danger")
            return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

    # -----------------------------------------------------------
    # مرحلة الـ GET (عرض الصفحة أو بعد الـ Redirect المباشر)
    # -----------------------------------------------------------
    # سحب بيانات المستخدم الجديد من الـ session إن وجدت وحذفها فوراً من الجلسة لضمان عدم تكرار ظهور النافذة عند التحديث
    new_user = session.pop('new_user_data', None)
    
    # جلب كافة الموردين لتغذية خيارات القائمة المنسدلة الذكية (Select2) في نموذج الموظفين التشغيليين
    suppliers = Supplier.query.all()
    
    return render_template(
        'admin_suppliers_add/admin_suppliers_add.html', 
        suppliers=suppliers, 
        new_user=new_user
    )
