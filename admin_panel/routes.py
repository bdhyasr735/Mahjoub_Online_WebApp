from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from core import db
from core.models import User, Supplier, Product
# استدعاء المحرك الجديد للربط مع قمرة
from core.qumra_connector import QumraConnector

# 1. إعداد الـ Blueprint بمسار القوالب الصحيح
admin_bp = Blueprint(
    'admin_panel', 
    __name__, 
    template_folder='templates'
)

qumra = QumraConnector()

# --- 📊 معالج السياق (تحديث العدادات في القائمة الجانبية آلياً) ---
@admin_bp.context_processor
def inject_counts():
    try:
        # حساب الموردين الذين ينتظرون "التعميد" (الاعتماد السيادي)
        pending_count = Supplier.query.filter_by(is_approved=False).count()
        return dict(pending_suppliers_count=pending_count)
    except:
        return dict(pending_suppliers_count=0)

# --- 2. بوابة دخول القائد علي محجوب ---
@admin_bp.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    if current_user.is_authenticated and session.get('user_type') == 'admin':
        return redirect(url_for('admin_panel.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, role='admin').first()

        # التحقق المشفر لضمان الأمان السيادي
        if user and check_password_hash(user.password, password):
            session.clear() 
            session['user_type'] = 'admin'
            login_user(user)
            flash('أهلاً بك أيها القائد علي في برج الرقابة السيادي للمنصة.', 'success')
            return redirect(url_for('admin_panel.dashboard'))
        else:
            flash('بيانات الولوج غير صحيحة.. الوصول للمنطقة السيادية مرفوض.', 'danger')
            
    return render_template('admin_panel/login.html')

# --- 3. لوحة التحكم (برج الرقابة الرئيسي) ---
@admin_bp.route('/', strict_slashes=False)
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if session.get('user_type') != 'admin':
        logout_user()
        return redirect(url_for('admin_panel.login'))

    try:
        # إحصائيات المنصة الشاملة
        s_count = Supplier.query.count()
        p_count = Product.query.count()
        # عرض آخر الموردين المنضمين لسرعة المراجعة
        latest_suppliers = Supplier.query.order_by(Supplier.id.desc()).limit(5).all()
        
        return render_template('admin_panel/dashboard.html', 
                               s_count=s_count, 
                               p_count=p_count, 
                               latest_suppliers=latest_suppliers)
    except Exception as e:
        print(f"⚠️ Error in admin dashboard: {e}")
        return f"خطأ تقني في غرفة القيادة: {str(e)}", 500

# --- 4. إدارة الموردين (غرفة التعميد السيادي) ---
@admin_bp.route('/manage-suppliers')
@login_required
def manage_suppliers():
    if session.get('user_type') != 'admin':
        return redirect(url_for('admin_panel.login'))
        
    pending_suppliers = Supplier.query.filter_by(is_approved=False).all()
    active_suppliers = Supplier.query.filter_by(is_approved=True).all()
    return render_template('admin_panel/suppliers_manage.html', 
                           pending=pending_suppliers, 
                           active=active_suppliers)

# --- 5. تعميد مورد (منحه الصلاحية) ---
@admin_bp.route('/approve-supplier/<int:supplier_id>')
@login_required
def approve_supplier(supplier_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('admin_panel.login'))
        
    supplier = Supplier.query.get_or_404(supplier_id)
    supplier.is_approved = True
    supplier.status = 'active'
    db.session.commit()
    flash(f'✅ تم تعميد المورد {supplier.trade_name} بنجاح.', 'success')
    return redirect(url_for('admin_panel.manage_suppliers'))

# --- 6. مراجعة ونشر المنتجات إلى قمرة ---
@admin_bp.route('/sync-products')
@login_required
def sync_now():
    if session.get('user_type') != 'admin':
        return redirect(url_for('admin_panel.login'))

    # جلب المنتجات غير النشطة التي رفعها الموردون
    pending_products = Product.query.filter_by(is_active=False).all()
    return render_template('admin_panel/product_review.html', products=pending_products)

# --- 7. تسجيل الخروج وتطهير الجلسة ---
@admin_bp.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('admin_panel.login'))
