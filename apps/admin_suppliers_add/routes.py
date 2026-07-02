# coding: utf-8
# 📂 apps/admin_suppliers_add/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
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
    data = request.get_json() or {}
    field_type = data.get('type')  # 'username' أو 'phone'
    value = data.get('value', '').strip()

    if not value:
        return jsonify({'available': False, 'message': '⚠️ الحقل فارغ'})

    # 1. التحقق من توفر اسم المستخدم
    if field_type == 'username':
        owner_exists = Supplier.query.filter_by(username=value).first()
        staff_exists = SupplierStaff.query.filter_by(username=value).first()
        
        if owner_exists or staff_exists:
            return jsonify({'available': False, 'message': 'اسم المستخدم مسجل مسبقاً في النظام'})
        return jsonify({'available': True, 'message': 'اسم المستخدم متاح للاستخدام'})

    # 2. التحقق من توفر وصحة رقم الهاتف
    elif field_type == 'phone':
        # الفحص بصيغة التعبيرات النمطية لضمان أنه 9 أرقام بدون مفتاح دولي
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
    """نقطة دخول موحدة وآمنة لإضافة مورد (مالك كيان) أو موظف تشغيلي مع أتمتة المحفظة."""
    
    if request.method == 'POST':
        action_type = request.form.get('action_type')  # 'owner' أو 'staff'
        temp_password = secrets.token_hex(4)  # توليد كلمة مرور عشوائية آمنة للمستخدم الجديد
        
        try:
            # ================= أولاً: معالجة إضافة المورد المالك =================
            if action_type == 'owner':
                username = request.form.get('username', '').strip()
                phone = request.form.get('phone', '').strip()
                trade_name = request.form.get('trade_name', '').strip()
                rank = request.form.get('rank', 'bronze')

                # جدار حماية خلفي (سرعة الاستجابة وصلاحية البيانات)
                if not re.match(r'^\d{9}$', phone):
                    flash("❌ خطأ: رقم هاتف المورد يجب أن يتكون من 9 أرقام فقط.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                # التحقق الأمني من عدم تكرار المعرفات الفريدة بالخلفية
                if Supplier.query.filter_by(username=username).first() or SupplierStaff.query.filter_by(username=username).first():
                    flash("❌ خطأ: اسم المستخدم مسجل مسبقاً لمورد أو موظف آخر.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                if Supplier.query.filter_by(phone=phone).first() or SupplierStaff.query.filter_by(phone=phone).first():
                    flash("❌ خطأ: رقم الهاتف مسجل مسبقاً في النظام.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                # 1. إنشاء كيان المورد
                new_supplier = Supplier(
                    username=username,
                    trade_name=trade_name,
                    rank=rank,
                    status='active'
                )
                new_supplier.phone = phone 
                new_supplier.set_password(temp_password)
                
                db.session.add(new_supplier)
                db.session.commit()  # الحفظ الأولي لإنشاء الـ ID وتوليد محفظته تلقائياً
                
                # 2. أتمتة إنشاء المحفظة المالية للمورد الجديد فوراً
                wallet_code = f"MAH-WEL{new_supplier.id}"
                new_wallet = SupplierWallet(
                    wallet_code=wallet_code,
                    supplier_id=new_supplier.id
                )
                db.session.add(new_wallet)
                db.session.commit()
                
                flash(f"✅ تم تسجيل المورد بنجاح: {new_supplier.trade_name} | رمز المحفظة المعتمد: {wallet_code} | كلمة المرور المؤقتة: {temp_password}", "success")
                
            # ================= ثانياً: معالجة إضافة الموظف التشغيلي =================
            elif action_type == 'staff':
                staff_username = request.form.get('staff_username', '').strip()
                staff_phone = request.form.get('staff_phone', '').strip()
                supplier_id = request.form.get('supplier_id')

                # جدار حماية خلفي لبيانات الموظف
                if not re.match(r'^\d{9}$', staff_phone):
                    flash("❌ خطأ: رقم هاتف الموظف يجب أن يتكون من 9 أرقام فقط.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                # فحص منع التكرار للموظف
                if Supplier.query.filter_by(username=staff_username).first() or SupplierStaff.query.filter_by(username=staff_username).first():
                    flash("❌ خطأ: اسم مستخدم الموظف مسجل مسبقاً بالحسابات المعتمدة.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                if Supplier.query.filter_by(phone=staff_phone).first() or SupplierStaff.query.filter_by(phone=staff_phone).first():
                    flash("❌ خطأ: رقم هاتف الموظف مسجل مسبقاً في النظام.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                # 3. إنشاء كائن الموظف التابع للمورد المختبر
                new_staff = SupplierStaff(
                    supplier_id=supplier_id,
                    username=staff_username,
                    phone=staff_phone,
                    role='worker'
                )
                new_staff.set_password(temp_password)
                
                db.session.add(new_staff)
                db.session.commit()
                
                flash(f"✅ تم إضافة الموظف بنجاح وتعيينه للعمل: {new_staff.username} | كلمة المرور المؤقتة: {temp_password}", "success")
            
            return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

        except IntegrityError:
            db.session.rollback()
            flash("❌ خطأ فني: البيانات المدخلة تسببت في تعارض مع قواعد البيانات (مكررة).", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"⚠️ حدث خطأ تقني غير متوقع: {str(e)}", "danger")

    # جلب كافة الموردين المتواجدين بالنظام لتمريرهم لخيارات تفعيل حسابات الموظفين (Dropdown Menu)
    suppliers = Supplier.query.all()
    return render_template('admin_suppliers_add/admin_suppliers_add.html', suppliers=suppliers)
