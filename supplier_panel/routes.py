from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import supplier_bp 
from .auth_logic import verify_supplier_credentials
from .decorators import sovereign_approval_required # 🛡️ حارس بوابة البرزخ

# --- 1. مسار تسجيل الدخول اللامركزي ---
@supplier_bp.route('/login', methods=['GET', 'POST'])
def login():
    # منع التداخل: إذا كان القائد (Admin) يحاول دخول بوابة المورد، يتم تبديل الجلسة
    if current_user.is_authenticated:
        if hasattr(current_user, 'wallet_balance'):
            return redirect(url_for('supplier_panel.dashboard'))
        else:
            logout_user() # تسجيل خروج الإدارة لفتح مجال للمورد

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('يرجى ملء كافة الحقول السيادية للدخول.', 'warning')
            return render_template('supplier_login.html')

        # التحقق من الهوية عبر المحقق الخارجي
        message, category, supplier = verify_supplier_credentials(username, password)
        
        if supplier: 
            login_user(supplier)
            flash(f'تم الولوج بنجاح.. أهلاً بك يا {supplier.name}', 'success')
            return redirect(url_for('supplier_panel.dashboard'))
        else:
            flash(message, category)
            
    return render_template('supplier_login.html')

# --- 2. لوحة التحكم (الترسانة الرقمية) ---
@supplier_bp.route('/dashboard')
@login_required
@sovereign_approval_required # 🛡️ الحارس السيادي: يحول المورد لصفحة الانتظار إذا لم يُعتمد
def dashboard():
    # استيراد الموديلات محلياً لمنع الخطأ 500 الناتج عن Circular Import
    from core.models.product import Product
    
    try:
        # 🔒 فحص الرتبة: التأكد أن المستخدم "مورد" (يملك محفظة)
        if not hasattr(current_user, 'wallet_balance'):
            logout_user()
            flash('عذراً، هذه المنطقة مخصصة لشركاء النجاح فقط.', 'danger')
            return redirect(url_for('supplier_panel.login'))
            
        # 📦 جلب المنتجات المرتبطة بهذا المورد حصراً
        try:
            my_products = Product.query.filter_by(supplier_id=current_user.id).all()
        except Exception as db_error:
            print(f"⚠️ تنبيه في قاعدة البيانات: {db_error}")
            my_products = [] # عرض صفحة فارغة بدلاً من الانهيار
            
        # تسليم البيانات للقالب
        return render_template('supplier_dashboard.html', products=my_products)
        
    except Exception as e:
        # إذا حدث خطأ في القالب أو البيانات، اطبع التفاصيل في الـ Terminal
        print(f"❌ خطأ داخلي في لوحة المورد: {e}")
        return f"خطأ في النظام (500): {e}", 500

# --- 3. خروج المورد وتأمين الترسانة ---
@supplier_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تأمين الجلسة وتشفير الخروج بنجاح.', 'info')
    return redirect(url_for('supplier_panel.login'))
