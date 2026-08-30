# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/routes.py

from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from apps.suppliers_auth_portal import suppliers_bp
from apps.models.supplier_db import Supplier
from apps.extensions import db


@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    """معالجة تسجيل دخول الموردين."""
    if current_user.is_authenticated:
        return redirect(url_for('suppliers_bp.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        if not username or not password:
            flash('الرجاء إدخال اسم المستخدم وكلمة المرور.', 'error')
            return render_template('supplier/login.html')

        try:
            # البحث عن المورد بواسطة اسم المستخدم أو رقم الهاتف
            supplier = Supplier.query.filter(
                (Supplier.username == username) | (Supplier.phone == username)
            ).first()

            if supplier and supplier.check_password(password):
                if supplier.status != 'active':
                    flash('حسابك معلق أو غير مفعّل. يرجى التواصل مع الإدارة.', 'error')
                    return render_template('supplier/login.html')

                # تسجيل الدخول عبر Flask-Login مع تعيين نوع المستخدم في الجلسة
                login_user(supplier, remember=remember)
                session_type_mapping = suppliers_bp  # تأكيد الجلسة
                from flask import session
                session['user_type'] = 'supplier'

                flash('تم تسجيل الدخول بنجاح. أهلاً بك!', 'success')
                return redirect(url_for('suppliers_bp.dashboard'))
            else:
                flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء تسجيل الدخول: {str(e)}', 'error')

    return render_template('supplier/login.html')


@suppliers_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة تحكم المورد الرئيسية."""
    from apps.models.wallet_db import SupplierWallet, WalletTransaction
    
    supplier_id = current_user.id
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    transactions = []
    
    if wallet:
        transactions = WalletTransaction.query.filter_by(wallet_id=wallet.id).order_by(WalletTransaction.created_at.desc()).limit(5).all()

    return render_template('supplier/dashboard.html', wallet=wallet, transactions=transactions)


@suppliers_bp.route('/register', methods=['GET', 'POST'])
def register():
    """طلب انضمام مورد جديد."""
    if request.method == 'POST':
        trade_name = request.form.get('trade_name', '').strip()
        owner_name = request.form.get('owner_name', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')

        if not trade_name or not owner_name or not phone or not password:
            flash('الرجاء تعبئة جميع الحقول الإجبارية.', 'error')
            return render_template('supplier/register.html')

        try:
            existing = Supplier.query.filter((Supplier.phone == phone) | (Supplier.username == phone)).first()
            if existing:
                flash('رقم الهاتف أو اسم المستخدم مستخدم مسبقاً.', 'error')
                return render_template('supplier/register.html')

            new_supplier = Supplier(
                username=phone,
                trade_name=trade_name,
                owner_name=owner_name,
                phone=phone,
                status='pending'  # يتطلب موافقة الإدارة
            )
            new_supplier.set_password(password)
            db.session.add(new_supplier)
            db.session.commit()

            flash('تم إرسال طلب انضمامك بنجاح. سيتم مراجعته وتفعيل الحساب قريباً.', 'success')
            return redirect(url_for('suppliers_bp.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء التسجيل: {str(e)}', 'error')

    return render_template('supplier/register.html')


@suppliers_bp.route('/forgot-password')
def forgot_password():
    """استعادة كلمة المرور للموردين."""
    flash('يرجى التواصل مع الإدارة الفنية لاستعادة كلمة المرور الخاصة بحسابك.', 'info')
    return redirect(url_for('suppliers_bp.login'))


@suppliers_bp.route('/logout')
@login_required
def logout():
    """تسجيل خروج المورد."""
    logout_user()
    from flask import session
    session.pop('user_type', None)
    flash('تم تسجيل الخروج بنجاح.', 'success')
    return redirect(url_for('suppliers_bp.login'))
