from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
# استيراد قاعدة البيانات والموديل من النواة (core)
from core import db
from core.models.user import User

class SupplierController:
    """
    متحكم منطق المصادقة واللوحات الخاص بالموردين (شركاء النجاح).
    يعتمد على موديل User للتحقق من الصلاحيات والحالة.
    """
    
    def __init__(self):
        pass

    def login_logic(self):
        # إذا كان المستخدم مسجلاً دخوله بالفعل ومورداً، يتم توجيهه للوحة التحكم مباشرة
        if current_user.is_authenticated and current_user.is_supplier():
            return redirect(url_for('supplier_panel.supplier_dashboard'))

        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False

            # البحث عن المستخدم بواسطة اسم المستخدم
            user = User.query.filter_by(username=username).first()

            # 1. التحقق من وجود المستخدم وكلمة المرور
            if not user or not user.check_password(password):
                flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')
                return render_template('supplier_panel/supplier_login.html')

            # 2. التحقق من الرتبة (يجب أن يكون مورد)
            if not user.is_supplier():
                flash('عذراً، هذا الحساب ليس لديه صلاحيات المورد.', 'warning')
                return render_template('supplier_panel/supplier_login.html')

            # 3. التحقق من حالة الحساب (يجب أن يكون مقبول)
            if not user.is_approved():
                flash('حسابك قيد المراجعة حالياً، يرجى التواصل مع الإدارة.', 'info')
                return render_template('supplier_panel/supplier_login.html')

            # تسجيل الدخول بنجاح
            login_user(user, remember=remember)
            return redirect(url_for('supplier_panel.supplier_dashboard'))

        return render_template('supplier_panel/supplier_login.html')

    @login_required
    def dashboard_logic(self):
        """
        لوحة تحكم شريك النجاح.
        يتم التحقق من أن المستخدم المسجل هو مورد بالفعل قبل عرض البيانات.
        """
        if not current_user.is_supplier():
            flash('غير مسموح لك بالوصول لهذه الصفحة.', 'danger')
            return redirect(url_for('supplier_panel.supplier_login'))
            
        # تأكد من وجود ملف dashboard.html داخل مجلد templates/supplier_panel/
        return render_template('supplier_panel/dashboard.html')

    def logout_logic(self):
        """إنهاء الجلسة والعودة لصفحة الدخول."""
        logout_user()
        flash('تم تسجيل الخروج بنجاح. ننتظر عودتك لشاشات "السوق الذكي" قريباً.', 'info')
        return redirect(url_for('supplier_panel.supplier_login'))
