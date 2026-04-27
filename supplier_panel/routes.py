from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
# استيراد البلوبرنت المعرف في __init__.py الخاص بالمجلد
from . import supplier_bp 
from .auth_logic import verify_supplier_credentials
from .decorators import sovereign_approval_required 
from core import db
from core.models import Product, Supplier, User 

# ملاحظة: تم إبقاء موصل قمرة اختيارياً لضمان عدم توقف السيرفر إذا لم يكن الملف جاهزاً
try:
    from core.qumra_connector import QumraConnector
    qumra = QumraConnector()
except ImportError:
    qumra = None

# --- 1. بوابة الدخول للموردين ---
@supplier_bp.route('/login', methods=['GET', 'POST'])
def login():
    # إذا كان المستخدم مسجلاً بالفعل كمورد، يتم توجيهه للوحة التحكم فوراً
    if current_user.is_authenticated:
        if session.get('user_type') == 'supplier':
            return redirect(url_for('supplier_panel.dashboard'))
        else:
            # إذا كان مسجلاً برتبة أخرى (كأدمن مثلاً)، يتم تطهير الجلسة للسماح بدخول المورد
            logout_user()
            session.clear()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('يرجى إدخال بيانات الهوية السيادية للمورد.', 'warning')
            return render_template('supplier_panel/login.html')

        # التحقق من الهوية عبر منطق المصادقة المركزية
        message, category, user = verify_supplier_credentials(username, password)
        
        if user and user.role == 'supplier': 
            session.permanent = True
            session['user_type'] = 'supplier' 
            login_user(user)
            
            # جلب الاسم التجاري للترحيب بالمورد
            supplier_name = user.supplier_profile.trade_name if user.supplier_profile else user.username
            flash(f'مرحباً بك يا {supplier_name} في منصة محجوب أونلاين.', 'success')
            return redirect(url_for('supplier_panel.dashboard'))
        else:
            flash(message or "عذراً، هذه البوابة للموردين فقط أو البيانات غير صحيحة.", 'danger')
            
    # العودة للقالب (تأكد أن الملف اسمه login.html داخل templates/supplier_panel/)
    return render_template('supplier_panel/login.html')

# --- 2. تسجيل الخروج ---
@supplier_bp.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    flash('تم تسجيل الخروج من الترسانة التجارية بنجاح.', 'info')
    return redirect(url_for('supplier_panel.login'))
