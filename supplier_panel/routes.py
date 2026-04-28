
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app as app

from flask_login import login_user, logout_user, login_required, current_user

from core import db

from core.models.user import User

# استيراد دالة التحقق

from .auth_logic import handle_supplier_auth



# 1. تعريف البلوبرينت

supplier_bp = Blueprint('supplier_panel', __name__, template_folder='templates')



# 2. مسار تسجيل الدخول (Login)

@supplier_bp.route('/login', methods=['GET', 'POST'])

def supplier_login():

    # منع المستخدم المسجل بالفعل من العودة لصفحة الدخول

    if current_user.is_authenticated:

        if current_user.role == 'supplier':

            return redirect(url_for('supplier_panel.supplier_dashboard'))

        elif current_user.role == 'admin':

            return redirect(url_for('admin_panel.admin_dashboard'))



    if request.method == 'POST':

        username = request.form.get('username')

        password = request.form.get('password')

        

        # استدعاء منطق التحقق

        user = handle_supplier_auth(username, password)

        

        if user:

            login_user(user)

            flash(f'مرحباً بك في نظام التوريد، {user.username}', 'success')

            return redirect(url_for('supplier_panel.supplier_dashboard'))

        

    return render_template('supplier_login.html')



# 3. لوحة تحكم المورد (Dashboard)

@supplier_bp.route('/dashboard')

@login_required

def supplier_dashboard():

    # فحص الرتبة والحالة لضمان أمن النظام السيادي

    if current_user.role != 'supplier' or current_user.status != 'approved':

        flash('وصول غير مصرح به أو الحساب قيد المراجعة.', 'danger')

        logout_user()

        return redirect(url_for('supplier_panel.supplier_login'))

        

    return render_template('supplier_dashboard.html', user=current_user)



# 4. تسجيل الخروج (Logout)

@supplier_bp.route('/logout')

@login_required

def supplier_logout():

    logout_user()

    flash('تم إنهاء الجلسة بنجاح.', 'info')

    return redirect(url_for('supplier_panel.supplier_login'))
