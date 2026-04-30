from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from admin_panel import admin_panel
from core.models import User, Supplier, Product, db
from core.utils.security import admin_required

# --- 1. بوابه الولوج السيادي (Login) ---
# المسار المرتبط بملف admin_panel/templates/login.html
@admin_panel.route('/login', methods=['GET', 'POST'])
def admin_login():
    # التحقق من الجلسة النشطة للقائد علي محجوب
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin_panel.admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # استعلام الهوية من قاعدة بيانات الترسانة
        user = User.query.filter_by(username=username, role='admin').first()

        # التحقق من مفتاح التشفير (Password)
        if user and user.check_password(password):
            login_user(user)
            flash('تم تفعيل الولوج السيادي بنجاح.. أهلاً بك أيها القائد.', 'success')
            return redirect(url_for('admin_panel.admin_dashboard'))
        else:
            flash('فشل في التحقق من الهوية.. تأكد من المعرف أو مفتاح التشفير.', 'danger')

    return render_template('login.html')

# --- 2. برج الرقابة المركزية (Dashboard) ---
# المسار المرتبط بملف admin_panel/templates/dashboard.html والهيكل base.html
@admin_panel.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    # جلب الإحصائيات الحية لتغذية نوافذ الإدارة
    stats = {
        'orders_count': 0, # سيتم ربطه بمحرك الطلبات لاحقاً
        's_count': Supplier.query.count(), # عدد شركاء الترسانة
        'total_balance': 0.00, # السيولة المركزية
        'p_count': Product.query.count() # طلبات قيد التدقيق
    }
    
    # سجل العمليات السيادية (Transactions) - فارغ حالياً للتهيئة
    recent_transactions = []
    
    return render_template('dashboard.html', 
                           orders_count=stats['orders_count'],
                           s_count=stats['s_count'],
                           total_balance=stats['total_balance'],
                           p_count=stats['p_count'],
                           transactions=recent_transactions)

# --- 3. نافذة حوكمة الموردين (Manage Suppliers) ---
# المسار المرتبط بملف admin_panel/templates/manage_suppliers.html
@admin_panel.route('/manage-suppliers')
@login_required
@admin_required
def manage_suppliers():
    # استعراض كافة الموردين للرقابة عليهم
    all_suppliers = Supplier.query.all()
    return render_template('manage_suppliers.html', suppliers=all_suppliers)

# --- 4. نافذة الاعتماد والتحقق (Supplier Verification) ---
# تفعيل الموردين ومنحهم صلاحية العرض في محجوب أونلاين
@admin_panel.route('/verify-supplier/<int:supplier_id>')
@login_required
@admin_required
def verify_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    supplier.is_verified = True
    db.session.commit()
    flash(f'تم منح الاعتماد الرسمي لمتجر: {supplier.store_name}.', 'success')
    return redirect(url_for('admin_panel.manage_suppliers'))

# --- 5. إنهاء الجلسة الآمنة (Logout) ---
@admin_panel.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم إغلاق البوابة السيادية بنجاح.', 'info')
    return redirect(url_for('admin_panel.admin_login'))
