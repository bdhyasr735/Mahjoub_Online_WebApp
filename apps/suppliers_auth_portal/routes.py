# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/routes.py
"""
مسارات المصادقة والتسجيل وإدارة لوحة تحكم الموردين - محجوب أونلاين
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_

from apps.extensions import db
from apps.models.supplier_db import Supplier
# تأكد من استيراد نموذج موظف المورد هنا أو تعديل مساره حسب مشروعك:
# from apps.models.supplier_employee_db import SupplierEmployee 
from apps.models.wallet_db import SupplierWallet
from apps.suppliers_auth_portal.otp_service import SupplierOTPService

suppliers_auth_bp = Blueprint(
    'suppliers_auth_bp', 
    __name__, 
    template_folder='templates',
    static_folder='static'
)

@suppliers_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """مسار تسجيل دخول الموردين وموظفيهم مع التحقق التفصيلي وتوافق الـ Frontend"""
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = request.get_json() or {}
        
        # التقاط الحقول القادمة من الـ Frontend الصحيح (identifier و user_type)
        login_input = data.get('identifier', '').strip().replace("+", "")
        password = data.get('password', '')
        user_type = data.get('user_type', 'supplier') # 'supplier' أو 'employee'

        if not login_input or not password:
            return jsonify({"success": False, "message": "الرجاء إدخال اسم المستخدم / رقم الهاتف وكلمة المرور."}), 400

        # الحالة الأولى: تسجيل دخول موظف مورد
        if user_type == 'employee':
            # تأكد من توفر نموذج SupplierEmployee، وفي حال كان غير مُعرف استبدله بالنموذج الخاص بك
            employee = SupplierEmployee.query.filter(
                or_(
                    SupplierEmployee.username == login_input,
                    SupplierEmployee.email == login_input,
                    SupplierEmployee.phone == login_input
                )
            ).first()

            if not employee:
                return jsonify({"success": False, "message": "معرف الموظف أو البريد الإلكتروني غير مسجل في المنصة اللامركزية."}), 404

            if not check_password_hash(employee.password_hash, password):
                return jsonify({"success": False, "message": "كلمة المرور غير صحيحة، يرجى المحاولة مرة أخرى."}), 401

            if getattr(employee, 'is_suspended', False):
                return jsonify({"success": False, "message": "تم توقيف حسابك الوظيفي نظراً لمخالفة اللوائح."}), 403

            login_user(employee, remember=data.get('remember_me', False))
            session['employee_id'] = employee.id
            session['supplier_id'] = employee.supplier_id # ربط الموظف بمورده الأساسي

            return jsonify({
                "success": True, 
                "message": "تم تسجيل الدخول بنجاح. جاري تحويلك إلى لوحة التحكم...", 
                "redirect_url": url_for('suppliers_auth_bp.dashboard')
            })

        # الحالة الثانية: تسجيل دخول حساب المورد الرئيسي (الافتراضي)
        else:
            supplier = Supplier.query.filter(
                or_(
                    Supplier.phone == login_input, 
                    Supplier.username == login_input,
                    Supplier.email == login_input
                )
            ).first()

            if not supplier:
                return jsonify({"success": False, "message": "رقم الهاتف أو اسم المستخدم أو البريد غير مسجل كمورد في المنصة اللامركزية."}), 404

            if not check_password_hash(supplier.password_hash, password):
                return jsonify({"success": False, "message": "كلمة المرور غير صحيحة، يرجى المحاولة مرة أخرى."}), 401

            if getattr(supplier, 'is_suspended', False):
                return jsonify({"success": False, "message": "تم توقيف لوحة التحكم نظراً لمخالفة ميثاق حوكمة الأسعار والتكلفة."}), 403

            login_user(supplier, remember=data.get('remember_me', False))
            session['supplier_id'] = supplier.id
            session['supplier_phone'] = supplier.phone

            return jsonify({
                "success": True, 
                "message": "تم تسجيل الدخول بنجاح. جاري تحويلك إلى لوحة التحكم...", 
                "redirect_url": url_for('suppliers_auth_bp.dashboard')
            })

    # الطلبات التقليدية العادية (Fallback في حال عدم تفعيل JavaScript)
    if request.method == 'POST':
        login_input = request.form.get('identifier', '').strip().replace("+", "")
        password = request.form.get('password', '')
        user_type = request.form.get('user_type', 'supplier')

        if user_type == 'employee':
            employee = SupplierEmployee.query.filter(
                or_(
                    SupplierEmployee.username == login_input, 
                    SupplierEmployee.email == login_input,
                    SupplierEmployee.phone == login_input
                )
            ).first()
            if not employee or not check_password_hash(employee.password_hash, password):
                flash('بيانات دخول الموظف غير صحيحة.', 'danger')
                return redirect(url_for('suppliers_auth_bp.login'))
            login_user(employee, remember=True)
            session['supplier_id'] = employee.supplier_id
        else:
            supplier = Supplier.query.filter(
                or_(
                    Supplier.phone == login_input, 
                    Supplier.username == login_input,
                    Supplier.email == login_input
                )
            ).first()
            if not supplier or not check_password_hash(supplier.password_hash, password):
                flash('رقم الهاتف أو اسم المستخدم غير صحيح.', 'danger')
                return redirect(url_for('suppliers_auth_bp.login'))
            login_user(supplier, remember=True)
            session['supplier_id'] = supplier.id
            session['supplier_phone'] = supplier.phone

        flash('تم تسجيل الدخول بنجاح.', 'success')
        return redirect(url_for('suppliers_auth_bp.dashboard'))

    return render_template('suppliers_auth_portal/login.html')


@suppliers_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """مسار تسجيل مورد جديد برقم الهاتف وإنشاء المحفظة المالية الذكية تلقائياً"""
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = request.get_json() or {}
        phone = data.get('phone', '').strip().replace("+", "")
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')

        if not phone or len(phone) != 9:
            return jsonify({"success": False, "message": "رقم الهاتف يجب أن يتكون من 9 أرقام صحيحة."}), 400

        if not password or len(password) < 8:
            return jsonify({"success": False, "message": "كلمة المرور يجب أن تكون 8 أحرف على الأقل."}), 400

        if password != confirm_password:
            return jsonify({"success": False, "message": "كلمتا المرور غير متطابقتين."}), 400

        existing_supplier = Supplier.query.filter_by(phone=phone).first()
        if existing_supplier:
            return jsonify({"success": False, "message": "رقم الهاتف مسجل مسبقاً، يمكنك تسجيل الدخول مباشرة."}), 400

        try:
            hashed_password = generate_password_hash(password)
            new_supplier = Supplier(
                phone=phone,
                password_hash=hashed_password,
                is_active=True
            )
            db.session.add(new_supplier)
            db.session.flush()

            new_wallet = SupplierWallet(
                supplier_id=new_supplier.id,
                balance=0.00,
                currency="YER",
                is_active=True
            )
            db.session.add(new_wallet)
            db.session.commit()

            client_ip = request.remote_addr
            user_agent = request.headers.get('User-Agent')
            SupplierOTPService.generate_and_send_otp(
                identifier=phone, 
                target_id=new_supplier.id, 
                target_type='supplier', 
                ip_address=client_ip, 
                user_agent=user_agent
            )

            return jsonify({
                "success": True,
                "message": "تم إنشاء الحساب والمحفظة المالية الذكية بنجاح!",
                "redirect_url": url_for('suppliers_auth_bp.login')
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"حدث خطأ داخلي أثناء عملية التسجيل: {str(e)}"}), 500

    return render_template('suppliers_auth_portal/register.html')


@suppliers_auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """مسار استعادة كلمة المرور عبر رقم الهاتف ورمز التحقق OTP"""
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip().replace("+", "")
        supplier = Supplier.query.filter_by(phone=phone).first()
        
        if not supplier:
            flash('رقم الهاتف غير مسجل في النظام.', 'danger')
            return redirect(url_for('suppliers_auth_bp.forgot_password'))

        otp_res = SupplierOTPService.generate_and_send_otp(
            identifier=phone,
            target_id=supplier.id,
            target_type='supplier_password_reset',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        if otp_res.get("success"):
            session['reset_phone'] = phone
            flash('تم إرسال رمز التحقق (OTP) إلى رقم واتساب الخاص بك بنجاح.', 'success')
            return redirect(url_for('suppliers_auth_bp.verify_reset_otp'))
        else:
            flash(otp_res.get("error", "فشل إرسال رمز التحقق."), 'danger')

    return render_template('suppliers_auth_portal/forgot_password.html')


@suppliers_auth_bp.route('/verify-reset-otp', methods=['GET', 'POST'])
def verify_reset_otp():
    """التحقق من رمز الاستعادة وتحديث كلمة المرور"""
    phone = session.get('reset_phone')
    if not phone:
        return redirect(url_for('suppliers_auth_bp.forgot_password'))

    if request.method == 'POST':
        entered_code = request.form.get('otp_code', '').strip()
        new_password = request.form.get('new_password', '')

        verify_res = SupplierOTPService.verify_otp(phone, entered_code)
        if not verify_res.get("success"):
            flash(verify_res.get("message", "رمز التحقق غير صحيح أو منتهي الصلاحية."), 'danger')
            return render_template('suppliers_auth_portal/verify_reset_otp.html')

        if not new_password or len(new_password) < 8:
            flash('كلمة المرور الجديدة يجب ألا تقل عن 8 أحرف.', 'danger')
            return render_template('suppliers_auth_portal/verify_reset_otp.html')

        supplier = Supplier.query.filter_by(phone=phone).first()
        if supplier:
            supplier.password_hash = generate_password_hash(new_password)
            db.session.commit()
            session.pop('reset_phone', None)
            flash('تم تحديث كلمة المرور بنجاح، يمكنك تسجيل الدخول الآن.', 'success')
            return redirect(url_for('suppliers_auth_bp.login'))

    return render_template('suppliers_auth_portal/verify_reset_otp.html')


@suppliers_auth_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة تحكم المورد المحمية"""
    wallet = SupplierWallet.query.filter_by(supplier_id=current_user.id).first()
    return render_template('suppliers_auth_portal/dashboard.html', wallet=wallet)


@suppliers_auth_bp.route('/logout')
def logout():
    """تسجيل خروج المورد وتنظيف الجلسة"""
    logout_user()
    session.clear()
    flash('تم تسجيل الخروج بنجاح.', 'success')
    return redirect(url_for('suppliers_auth_bp.login'))


def init_app(app):
    """دالة تسجيل الـ Blueprint الخاص ببوابة الموردين في التطبيق الرئيسي"""
    app.register_blueprint(suppliers_auth_bp, url_prefix='/supplier')
