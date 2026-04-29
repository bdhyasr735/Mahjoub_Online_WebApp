from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
# استيراد الموديل والمكتبة الخاصة بقاعدة البيانات من النواة
from core import db
from core.models.user import User  # تأكد من أن مسار موديل المستخدم صحيح

class SupplierController:
    """
    متحكم منطق المصادقة الخاص بالموردين (شركاء النجاح).
    تم تصميمه لضمان أمن العمليات داخل السوق الذكي.
    """
    
    def __init__(self):
        # يمكن إضافة إعدادات التشفير أو الترددات الأمنية هنا مستقبلاً
        pass

    def login_logic(self):
        # إذا كان المستخدم مسجلاً دخوله بالفعل، يتم توجيهه للوحة التحكم
        if current_user.is_authenticated:
            return redirect(url_for('supplier_panel.supplier_dashboard'))

        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False

            # البحث عن المستخدم في قاعدة البيانات
            user = User.query.filter_by(email=email).first()

            # التحقق من كلمة المرور (تأكد أن الموديل يحتوي على دالة check_password)
            if not user or not user.check_password(password):
                flash('يرجى التحقق من بيانات الدخول والمحاولة مرة أخرى.', 'danger')
                return render_template('supplier_panel/supplier_login.html')

            # تسجيل الدخول
            login_user(user, remember=remember)
            
            # توجيه المورد إلى لوحته الخاصة
            return redirect(url_for('supplier_panel.supplier_dashboard'))

        return render_template('supplier_panel/supplier_login.html')

    def dashboard_logic(self):
        """عرض إحصائيات المورد وسلاسل التوريد الخاصة به."""
        return render_template('supplier_panel/dashboard.html')

    def logout_logic(self):
        """إنهاء الجلسة بأمان."""
        logout_user()
        flash('تم تسجيل الخروج بنجاح. ننتظر عودتك قريباً.', 'info')
        return redirect(url_for('supplier_panel.supplier_login'))

    def profile_logic(self):
        """إدارة بيانات المورد التقنية والشخصية."""
        return render_template('supplier_panel/profile.html')
