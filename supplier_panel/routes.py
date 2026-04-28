from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, logout_user, current_user
from . import supplier_bp
from .auth_logic import handle_supplier_auth
from .decorators import supplier_required
from core.models.product import Product # تأكد من استيراد موديل المنتجات

# --- 1. مسار تسجيل الدخول ---
@supplier_bp.route('/login', methods=['GET', 'POST'])
def login():
    # إذا كان المورد مسجلاً بالفعل، وجهه لمكانه الصحيح
    if current_user.is_authenticated and current_user.role == 'supplier':
        if current_user.status == 'approved':
            return redirect(url_for('supplier_panel.dashboard'))
        return redirect(url_for('supplier_panel.waiting_approval'))

    if request.method == 'POST':
        # استدعاء المنطق من ملف auth_logic.py المنفصل
        user = handle_supplier_auth(request.form.get('username'), request.form.get('password'))
        if user:
            if user.status == 'approved':
                return redirect(url_for('supplier_panel.dashboard'))
            return redirect(url_for('supplier_panel.waiting_approval'))
            
    return render_template('supplier_panel/supplier_login.html')

# --- 2. مسار غرفة الانتظار (المنصة اللامركزية) ---
@supplier_bp.route('/waiting-approval')
@login_required
def waiting_approval():
    # إذا وافق علي محجوب على المورد وهو فاتح هذه الصفحة، يتم توجيهه تلقائياً
    if current_user.status == 'approved':
        return redirect(url_for('supplier_panel.dashboard'))
    return render_template('supplier_panel/waiting_approval.html')

# --- 3. لوحة تحكم المورد (محمية بالديكوريتور) ---
@supplier_bp.route('/dashboard')
@supplier_required # الحماية من ملف decorators.py
def dashboard():
    # جلب منتجات المورد الخاص بـ "محجوب أونلاين"
    products = Product.query.filter_by(supplier_id=current_user.id).all()
    return render_template('supplier_panel/dashboard.html', products=products)

# --- 4. تسجيل الخروج الآمن ---
@supplier_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('🔒 تم تأمين الجلسة والخروج من المنصة اللامركزية بنجاح.', 'info')
    return redirect(url_for('supplier_panel.login'))
