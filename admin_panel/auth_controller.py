from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
# استيراد موديل المستخدم من النواة
from core.models.user import User

class AdminAuthController:
    """
    متحكم إدارة النظام (السوق الذكي).
    مسؤول عن التحقق من صلاحيات المسؤولين وضمان حوكمة المنصة.
    """
    
    def __init__(self):
        pass

    def login_logic(self):
        # 1. إذا كان المسؤول مسجلاً دخوله بالفعل، يتم توجيهه للوحة التحكم مباشرة
        if current_user.is_authenticated:
            if current_user.is_admin():
                return redirect(url_for('admin_panel.admin_dashboard'))
            else:
                # إذا كان المستخدم مسجل دخول برتبة أخرى (مثل مورد)، يتم تسجيل خروجه أولاً
                logout_user()

        if request.method == 'POST':
            # ملاحظة: نستخدم 'username' ليتوافق مع الموديل الخاص بك في core/models/user.py
            username = request.form.get('username')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False

            # البحث عن المستخدم في قاعدة البيانات بواسطة اسم المستخدم
            user = User.query.filter_by(username=username).first()

            # 2. التحقق من صحة البيانات (اسم المستخدم وكلمة المرور المشفرة)
            if not user or not user.check_password(password):
                flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')
                return render_template('admin_panel/login.html')

            # 3. التحقق من الرتبة: يجب أن يكون الحساب برتبة 'admin'
            if not user.is_admin():
                flash('عذراً، هذا الحساب لا يمتلك صلاحيات وصول إدارية.', 'warning')
                return render_template('admin_panel/login.html')

            # 4. تسجيل الدخول بنجاح عبر Flask-Login
            login_user(user, remember=remember)
            
            # التوجيه إلى لوحة التحكم الرئيسية للإدارة
            return redirect(url_for('admin_panel.admin_dashboard'))

        # عرض صفحة تسجيل الدخول (GET request)
        return render_template('admin_panel/login.html')

    def dashboard_logic(self):
        """منطق لوحة التحكم المركزية"""
        return render_template('admin_panel/dashboard.html')

    def suppliers_logic(self):
        """منطق إدارة الموردين (شركاء النجاح)"""
        return render_template('admin_panel/suppliers_management.html')

    def logout_logic(self):
        """إنهاء جلسة الإدارة بأمان"""
        logout_user()
        flash('تم تسجيل الخروج من لوحة الإدارة بنجاح.', 'success')
        return redirect(url_for('admin_panel.admin_login'))
