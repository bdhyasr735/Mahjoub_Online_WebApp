from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, login_user, logout_user
from . import admin_bp

# استيراد الموديلات بشكل آمن لتجنب تضارب MetaData
# يفضل الاستيراد من المسار المباشر للموديل
from core.models.user import User

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """بوابة الدخول لسيادة القائد"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # البحث عن القائد علي محجوب في الترسانة
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # التأكد من رتبة المسؤول وحالة الحساب قبل السماح بالدخول
            if user.role == 'admin' and user.is_active_account:
                login_user(user)
                return redirect(url_for('admin.admin_dashboard'))
            else:
                flash("⚠️ تنبيه: الحساب لا يملك صلاحيات سيادية.")
        else:
            flash("❌ خطأ في بيانات الدخول.")
            
    return render_template('login.html')

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    """لوحة التحكم المركزية لمنصة محجوب أونلاين"""
    
    # التحقق الإضافي لضمان وصول القائد فقط
    if current_user.role != 'admin':
        return "غير مسموح بالدخول لغير القائد", 403

    context = {
        'orders_count': "1,250",      
        's_count': "48",              
        'total_balance': "15.5K",     
        'p_count': "12",               
        'admin_name': current_user.username,
        
        'transactions': [
            {
                'supplier_name': 'مورد عدن المركزي',
                'type': 'توريد بضائع',
                'amount': 2500,
                'date': '2026-05-02',
                'status': 'مكتمل'
            },
            {
                'supplier_name': 'شركة المخا للاستيراد',
                'type': 'سحب سيولة',
                'amount': -450,
                'date': '2026-05-01',
                'status': 'قيد التدقيق'
            },
            {
                'supplier_name': 'موزع الخوخة الرقمي',
                'type': 'تسوية عمولة',
                'amount': 120,
                'date': '2026-04-30',
                'status': 'مكتمل'
            }
        ]
    }
    
    return render_template('dashboard.html', **context)

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.admin_login'))
