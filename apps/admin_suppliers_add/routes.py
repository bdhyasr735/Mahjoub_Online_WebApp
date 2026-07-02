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
import re  # مكتبة التحقق من النصوص والأرقام

admin_suppliers_add_bp = Blueprint(
    'admin_suppliers_add_bp', 
    __name__, 
    template_folder='templates'
)

# -----------------------------------------------------------
# API جديد: للتحقق اللحظي في المتصفح (يُظهر الصح ✅ والخطأ ❌)
# -----------------------------------------------------------
@admin_suppliers_add_bp.route('/check_availability', methods=['POST'])
@login_required
def check_availability():
    data = request.get_json()
    field_type = data.get('type') # 'username' or 'phone'
    value = data.get('value')

    if not value:
        return jsonify({'available': False, 'message': ''})

    if field_type == 'username':
        # نتحقق من عدم وجود الاسم في جدول الموردين أو الموظفين
        owner_exists = Supplier.query.filter_by(username=value).first()
        staff_exists = SupplierStaff.query.filter_by(username=value).first()
        
        if owner_exists or staff_exists:
            return jsonify({'available': False, 'message': '❌ الاسم مسجل مسبقاً'})
        return jsonify({'available': True, 'message': '✅ متاح'})

    elif field_type == 'phone':
        # التحقق من أن الهاتف 9 أرقام فقط
        if not re.match(r'^\d{9}$', value):
            return jsonify({'available': False, 'message': '❌ يجب أن يكون 9 أرقام'})
            
        owner_exists = Supplier.query.filter_by(phone=value).first()
        staff_exists = SupplierStaff.query.filter_by(phone=value).first()
        
        if owner_exists or staff_exists:
            return jsonify({'available': False, 'message': '❌ الرقم مسجل مسبقاً'})
        return jsonify({'available': True, 'message': '✅ متاح'})

    return jsonify({'available': False})


# -----------------------------------------------------------
# مسار الحفظ الرئيسي
# -----------------------------------------------------------
@admin_suppliers_add_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier_or_staff():
    """نقطة دخول موحدة لإضافة مورد (مالك) أو موظف مع أتمتة المحفظة."""
    
    if request.method == 'POST':
        action_type = request.form.get('action_type') # 'owner' or 'staff'
        temp_password = secrets.token_hex(4) 
        
        try:
            if action_type == 'owner':
                username = request.form.get('username')
                phone = request.form.get('phone')

                # حماية خلفية: التأكد من الهاتف 9 أرقام
                if not re.match(r'^\d{9}$', phone):
                    flash("❌ خطأ: رقم هاتف المورد يجب أن يتكون من 9 أرقام فقط.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                # حماية خلفية: منع التكرار في جميع الجداول
                if Supplier.query.filter_by(username=username).first() or SupplierStaff.query.filter_by(username=username).first():
                    flash("❌ خطأ: اسم المستخدم مسجل مسبقاً لمورد أو موظف.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                # 1. إنشاء المورد (المالك)
                new_supplier = Supplier(
                    username=username,
                    trade_name=request.form.get('trade_name'),
                    rank=request.form.get('rank', 'bronze'),
                    status='active'
                )
                new_supplier.phone = phone 
                new_supplier.set_password(temp_password)
                
                db.session.add(new_supplier)
                db.session.commit() # حفظ المورد أولاً للحصول على ID
                
                # 2. أتمتة إنشاء المحفظة فوراً
                wallet_code = f"MAH-WEL{new_supplier.id}"
                new_wallet = SupplierWallet(
                    wallet_code=wallet_code,
                    supplier_id=new_supplier.id
                )
                db.session.add(new_wallet)
                db.session.commit()
                
                flash(f"✅ تم تسجيل المورد: {new_supplier.trade_name} | المحفظة: {wallet_code} | كلمة المرور: {temp_password}", "success")
                
            elif action_type == 'staff':
                staff_username = request.form.get('staff_username')
                staff_phone = request.form.get('staff_phone')

                # حماية خلفية: التأكد من الهاتف 9 أرقام
                if not re.match(r'^\d{9}$', staff_phone):
                    flash("❌ خطأ: رقم هاتف الموظف يجب أن يتكون من 9 أرقام فقط.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                # حماية خلفية: منع التكرار في جميع الجداول
                if Supplier.query.filter_by(username=staff_username).first() or SupplierStaff.query.filter_by(username=staff_username).first():
                    flash("❌ خطأ: اسم مستخدم الموظف مسجل مسبقاً.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                # 3. إنشاء الموظف
                new_staff = SupplierStaff(
                    supplier_id=request.form.get('supplier_id'),
                    username=staff_username,
                    phone=staff_phone,
                    role='worker'
                )
                new_staff.set_password(temp_password)
                
                db.session.add(new_staff)
                db.session.commit()
                
                flash(f"✅ تم إضافة الموظف: {new_staff.username} | كلمة المرور: {temp_password}", "success")
            
            return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

        except IntegrityError:
            db.session.rollback()
            flash("❌ خطأ: اسم المستخدم أو الهاتف مسجل مسبقاً في النظام.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"⚠️ حدث خطأ تقني: {str(e)}", "danger")

    suppliers = Supplier.query.all()
    return render_template('admin_suppliers_add/admin_suppliers_add.html', suppliers=suppliers)
