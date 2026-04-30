from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from admin_panel import admin_panel
from core.models import User, Supplier, Product, db
from core.utils.security import admin_required

# --- بوابة تسجيل الدخول (نظام الولوج السيادي) ---
@admin_panel.route('/login', methods=['GET', 'POST'])
def admin_login():
    # إذا كان القائد مسجلاً دخوله بالفعل، يتم توجيهه لمركز المراقبة
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin_panel.admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # البحث عن حساب الأدمن في قاعدة بيانات Render
        user = User.query.filter_by(username=username, role='admin').first()

        # التحقق من مفتاح التشفير
        if user and user.check_password(password):
            login_user(user)
            flash('تم تفعيل الولوج السيادي بنجاح.. أهلاً بك أيها القائد.', 'success')
            return redirect(url_for('admin_panel.admin_dashboard'))
        else:
            flash('فشل في التحقق من الهوية.. تأكد من المعرف أو مفتاح التشفير.', 'danger')

    return render_template('login.html')

# --- مركز المراقبة (لوحة التحكم المركزية) ---
@admin_panel.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    # إحصائيات حية من الترسانة متوافقة مع Dashboard.html
    stats_data = {
        'orders_count': 0, # سيتم ربطه بجدول الطلبات لاحقاً
        's_count': Supplier.query.count(),
        'total_balance': 0.00, # محرك السيولة المالية
        'p_count': Product.query.count()
    }
    
    # العمليات الأخيرة (سجلات النشاط)
    recent_transactions = []
    
    return render_template('dashboard.html', 
                           orders_count=stats_data['orders_count'],
                           s_count=stats_data['s_count'],
                           total_balance=stats_data['total_balance'],
                           p_count=stats_data['p_count'],
                           transactions=recent_transactions)

# --- حوكمة الموردين (إدارة الشركاء) ---
@admin_panel.route('/manage-suppliers')
@login_required
@admin_required
def manage_suppliers():
    # جلب جميع الموردين المسجلين في النظام
    all_suppliers = Supplier.query.all()
    return render_template('manage_suppliers.html', suppliers=all_suppliers)

# --- نظام الاعتماد والتحقق السيادي ---
@admin_panel.route('/verify-supplier/<int:supplier_id>')
@login_required
@admin_required
def verify_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    supplier.is_verified = True
    db.session.commit()
    flash(f'تم منح الاعتماد الرسمي لمتجر: {supplier.store_name}.', 'success')
    return redirect(url_for('admin_panel.manage_suppliers'))

# --- إنهاء الجلسة الآمنة ---
@admin_panel.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم إغلاق البوابة السيادية بنجاح.', 'info')
    return redirect(url_for('admin_panel.admin_login'))
