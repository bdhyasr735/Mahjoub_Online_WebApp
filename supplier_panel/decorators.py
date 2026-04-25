from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import supplier_bp
from .auth_logic import verify_supplier_credentials
from .decorators import sovereign_approval_required

# 1. مسار تسجيل الدخول (البوابة السيادية)
@supplier_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('supplier_panel.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # استخدام المنطق الذي فحصناه سابقاً
        message, category, supplier = verify_supplier_credentials(username, password)
        
        if supplier:
            login_user(supplier)
            flash(message, category)
            return redirect(url_for('supplier_panel.dashboard'))
        
        flash(message, category)
    
    return render_template('login.html')

# 2. مسار لوحة التحكم (الداشبورد)
# نستخدم الحارس لضمان أن المورد "معتمد" قبل رؤية الأرقام
@supplier_bp.route('/dashboard')
@login_required
@sovereign_approval_required
def dashboard():
    # جلب المنتجات الخاصة بهذا المورد فقط لعرضها في الداشبورد
    products = current_user.products if hasattr(current_user, 'products') else []
    return render_template('dashboard.html', products=products)

# 3. مسار صفحة الانتظار (البرزخ الرقمي)
# هذا المسار يظهر فقط للموردين الذين لم يتم اعتمادهم بعد
@supplier_bp.route('/waiting-room')
@login_required
def waiting_room():
    if current_user.is_approved:
        return redirect(url_for('supplier_panel.dashboard'))
    return render_template('waiting_approval.html')

# 4. تسجيل الخروج
@supplier_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("تم تسجيل الخروج من الترسانة بأمان.", "info")
    return redirect(url_for('supplier_panel.login'))
