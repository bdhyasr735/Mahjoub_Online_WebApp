# coding: utf-8
# 📂 apps/admin_suppliers_add/routes.py

import secrets
import re
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session, abort
from flask_login import login_required
from apps.extensions import db
from apps import csrf
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.wallet_db import SupplierWallet

# إعداد الـ Blueprint
admin_suppliers_add_bp = Blueprint(
    'admin_suppliers_add_bp', 
    __name__, 
    template_folder='templates'
)

# -----------------------------------------------------------
# دالة مساعدة للتحقق من وجود المستخدم
# -----------------------------------------------------------
def check_user_exists(username=None, phone=None):
    if username:
        return Supplier.query.filter_by(username=username).first() or \
               SupplierStaff.query.filter_by(username=username).first()
    if phone:
        return Supplier.query.filter_by(phone=phone).first() or \
               SupplierStaff.query.filter_by(phone=phone).first()
    return None

# -----------------------------------------------------------
# API: للتحقق اللحظي من توفر البيانات
# -----------------------------------------------------------
@admin_suppliers_add_bp.route('/check_availability', methods=['POST'])
@csrf.exempt 
@login_required
def check_availability():
    data = request.get_json() or {}
    field_type = data.get('type')
    value = data.get('value', '').strip()

    if not value:
        return jsonify({'available': False, 'message': '⚠️ الحقل فارغ'})

    if field_type == 'username':
        if check_user_exists(username=value):
            return jsonify({'available': False, 'message': 'اسم المستخدم مسجل مسبقاً'})
        return jsonify({'available': True, 'message': 'متاح'})

    elif field_type == 'phone':
        if not re.match(r'^\d{9}$', value):
            return jsonify({'available': False, 'message': 'يجب أن يكون 9 أرقام'})
        if check_user_exists(phone=value):
            return jsonify({'available': False, 'message': 'رقم الهاتف مرتبط بحساب آخر'})
        return jsonify({'available': True, 'message': 'متاح'})

    elif field_type == 'trade_name':
        if len(value) < 3:
            return jsonify({'available': False, 'message': 'الاسم قصير جداً'})
        if Supplier.query.filter_by(trade_name=value).first():
            return jsonify({'available': False, 'message': 'هذا الاسم التجاري مسجل مسبقاً'})
        return jsonify({'available': True, 'message': 'اسم المتجر متاح'})

    return jsonify({'available': False, 'message': 'طلب غير مدعوم'})

# -----------------------------------------------------------
# المسار الرئيسي: حفظ المورد أو الموظف
# -----------------------------------------------------------
@admin_suppliers_add_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier_or_staff():
    if request.method == 'POST':
        if request.form.get('hp_field'):
            abort(403) 

        action_type = request.form.get('action_type')
        temp_password = secrets.token_hex(4) 
        registration_time = datetime.utcnow()
        
        try:
            # --- معالجة المورد المالك (Owner) ---
            if action_type == 'owner':
                username = request.form.get('username', '').strip()
                phone = request.form.get('phone', '').strip()
                trade_name = request.form.get('trade_name', '').strip()
                owner_name = request.form.get('owner_name', '').strip() # استلام اسم المالك
                rank = request.form.get('rank', 'bronze')

                if not re.match(r'^\d{9}$', phone) or check_user_exists(username=username, phone=phone) or Supplier.query.filter_by(trade_name=trade_name).first():
                    flash("❌ البيانات غير صالحة أو مسجلة مسبقاً في النظام.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                new_supplier = Supplier(
                    username=username, 
                    trade_name=trade_name,
                    owner_name=owner_name, # حفظ اسم المالك
                    rank=rank, 
                    status='active',
                    registration_date=registration_time
                )
                new_supplier.phone = phone 
                new_supplier.set_password(temp_password)
                
                db.session.add(new_supplier)
                db.session.flush() # الحصول على ID قبل الـ Commit
                
                # إنشاء المحفظة تلقائياً
                wallet_code = f"MAH-WEL{new_supplier.id}"
                new_wallet = SupplierWallet(
                    wallet_code=wallet_code, 
                    supplier_id=new_supplier.id
                )
                db.session.add(new_wallet)
                db.session.commit()
                
                # تخزين البيانات في الجلسة مع اسم المالك ورقم المحفظة
                session['new_user_data'] = {
                    'type': 'مورد جديد',
                    'trade_name': trade_name,
                    'owner_name': owner_name, # إضافة اسم المالك للجلسة
                    'wallet_code': wallet_code, # إضافة كود المحفظة للجلسة
                    'username': username, 
                    'password': temp_password
                }
                flash(f"✅ تم تسجيل المورد: {trade_name}", "success")

            # --- معالجة الموظف التشغيلي (Staff) ---
            elif action_type == 'staff':
                username = request.form.get('staff_username', '').strip()
                phone = request.form.get('staff_phone', '').strip()
                supplier_id = request.form.get('supplier_id')

                if not supplier_id or not re.match(r'^\d{9}$', phone) or check_user_exists(username=username, phone=phone):
                    flash("❌ بيانات الموظف غير صحيحة أو مستخدمة.", "danger")
                    return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

                new_staff = SupplierStaff(
                    supplier_id=supplier_id, 
                    username=username, 
                    phone=phone, 
                    role='worker', 
                    registration_date=registration_time
                )
                new_staff.set_password(temp_password)
                db.session.add(new_staff)
                db.session.commit()
                
                parent = Supplier.query.get(supplier_id)
                session['new_user_data'] = {
                    'type': 'موظف تشغيلي',
                    'trade_name': parent.trade_name if parent else "غير محدد", 
                    'username': username, 
                    'password': temp_password
                }
                flash("✅ تم إضافة الموظف بنجاح.", "success")
            
            return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error in add_supplier_or_staff: {e}")
            flash(f"⚠️ حدث خطأ تقني غير متوقع.", "danger")
            return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

    # عرض الصفحة (GET)
    new_user = session.pop('new_user_data', None)
    suppliers = Supplier.query.order_by(Supplier.trade_name.asc()).all()
    return render_template('admin_suppliers_add/admin_suppliers_add.html', suppliers=suppliers, new_user=new_user)
