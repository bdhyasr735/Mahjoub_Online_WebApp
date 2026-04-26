from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from . import supplier_bp 
from .auth_logic import verify_supplier_credentials
from .decorators import sovereign_approval_required 

# --- 1. مسار تسجيل الدخول اللامركزي ---
@supplier_bp.route('/login', methods=['GET', 'POST'])
def login():
    # منع التداخل السيادي: إذا كان المستخدم مسجل دخوله بالفعل
    if current_user.is_authenticated:
        if session.get('user_type') == 'supplier':
            return redirect(url_for('supplier_panel.dashboard'))
        else:
            # تطهير أي جلسة سابقة (أدمن أو غيره) لفتح مسار المورد
            logout_user()
            session.clear()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('يرجى ملء كافة الحقول السيادية للدخول.', 'warning')
            return render_template('supplier_panel/supplier_login.html') # تحديد المجلد

        # التحقق من الهوية عبر المحقق الخارجي
        message, category, supplier = verify_supplier_credentials(username, password)
        
        if supplier: 
            # 🛡️ الختم السيادي: تحديد نوع الهوية في الجلسة لضمان التوجيه الصحيح
            session.permanent = True
            session['user_type'] = 'supplier'
            
            login_user(supplier)
            flash(f'تم الولوج بنجاح.. أهلاً بك في ترسانتك يا {supplier.name}', 'success')
            
            return redirect(url_for('supplier_panel.dashboard'))
        else:
            flash(message, category)
            
    # تأكد أن ملف supplier_login.html موجود داخل supplier_panel/templates/supplier_panel/
    return render_template('supplier_panel/supplier_login.html')

# --- 2. لوحة التحكم (الترسانة الرقمية) ---
@supplier_bp.route('/dashboard')
@login_required
@sovereign_approval_required 
def dashboard():
    from core.models.product import Product
    
    try:
        # تأمين المسار: التأكد أن المستخدم يحمل وسم "مورد" حصراً
        if session.get('user_type') != 'supplier':
            session.clear()
            logout_user()
            flash('عذراً، هذه المنطقة مخصصة للموردين المعتمدين فقط.', 'danger')
            return redirect(url_for('supplier_panel.login'))
            
        # جلب منتجات المورد بناءً على معرفه الفريد
        try:
            my_products = Product.query.filter_by(supplier_id=current_user.id).all()
        except Exception as db_error:
            print(f"⚠️ تنبيه في قاعدة البيانات: {db_error}")
            my_products = []
            
        # التعديل الجوهري: تحديد المسار الكامل للقالب لمنع تداخل الإدارة
        return render_template('supplier_panel/dashboard.html', products=my_products)
        
    except Exception as e:
        print(f"❌ خطأ داخلي في لوحة المورد: {e}")
        return f"خطأ في النظام (500): {str(e)}", 500

# --- 3. صفحة الانتظار (تحديث تلقائي للحالة) ---
@supplier_bp.route('/waiting-room')
@login_required
def waiting_room():
    """
    كسر التناقض: فحص الحالة من قاعدة البيانات مباشرة لتجاوز "كاش" الجلسة
    """
    from core.models.supplier import Supplier
    
    # جلب بيانات طازجة للتأكد من حالة الاعتماد الحالية
    fresh_data = Supplier.query.get(current_user.id)
    
    if fresh_data and fresh_data.is_approved:
        flash('تهانينا! تم تفعيل حسابك سيادياً من قبل الإدارة.', 'success')
        return redirect(url_for('supplier_panel.dashboard'))
    
    return render_template('supplier_panel/waiting_approval.html')

# --- 4. خروج المورد وتأمين الجلسة ---
@supplier_bp.route('/logout')
@login_required
def logout():
    # إنهاء الجلسة وتطهير الوسم السيادي تماماً
    session.pop('user_type', None)
    session.clear()
    logout_user()
    flash('تم تأمين الجلسة وتشفير الخروج بنجاح.', 'info')
    return redirect(url_for('supplier_panel.login'))
