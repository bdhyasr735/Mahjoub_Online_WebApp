import os
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import logout_user, login_required, current_user
from sqlalchemy import or_
from datetime import datetime
from functools import wraps

# الاستيراد من الهيكلية المعتمدة لترسانة محجوب أونلاين
from core.extensions import db 
from core.models.supplier import Supplier, SupplierStaff
from core.models.user import User

from . import admin_bp
from .auth import handle_admin_login

# --- 1. بروتوكول التحقق السيادي (Sovereign Auth) ---
def is_admin_sovereign():
    """ يضمن أن المؤسس علي محجوب (أو من يحمل رتبة Admin) فقط يمكنه الوصول. """
    return current_user.is_authenticated and getattr(current_user, 'role', '').lower() == 'admin'

def admin_api_required(f):
    """ تأمين الـ APIs لضمان أن الاستدعاءات تتم من داخل مركز القيادة فقط """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_sovereign():
            return jsonify({"status": "error", "message": "Access Denied: Sovereign Auth Required"}), 403
        return f(*args, **kwargs)
    return decorated_function

# --- 2. بوابة الدخول ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if is_admin_sovereign(): 
        return redirect(url_for('admin.admin_dashboard'))
    return handle_admin_login()

# --- 3. مركز القيادة الإحصائي (Dashboard) ---
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if not is_admin_sovereign():
        return redirect(url_for('admin.login'))
    
    try:
        stats = {
            'users_count': User.query.count() if User else 1,
            'suppliers_count': Supplier.query.count() if Supplier else 0,
            'now': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # محاولة جلب عدد الطلبات من موديل الأعمال
        try:
            from core.models.business import Order
            stats['orders_count'] = Order.query.count()
        except:
            stats['orders_count'] = 0

        return render_template('dashboard.html', **stats)
    except Exception as e:
        return render_template('dashboard.html', users_count=1, suppliers_count=0, orders_count=0, now="إيقاع النظام مستقر")

# --- 4. إدارة الموردين (عرض الواجهة الرئيسية) ---
@admin_bp.route('/manage-suppliers')
@login_required
def manage_suppliers():
    if not is_admin_sovereign():
        return redirect(url_for('admin.login'))
    return render_template('manage_suppliers.html')

# --- 5. محرك البحث السيادي (API للترسانة) ---
@admin_bp.route('/api/suppliers/search')
@admin_api_required
def api_suppliers_search():
    """ المغذي الرئيسي لمحرك البحث في sovereign_engine.js """
    query_str = request.args.get('q', '').strip()
    province = request.args.get('province', '')
    district = request.args.get('district', '')
    tier = request.args.get('tier', '')
    status = request.args.get('status', '')

    db_query = Supplier.query

    # منطق البحث المرن
    if query_str and query_str != '#':
        search_filter = or_(
            Supplier.owner_name.icontains(query_str),
            Supplier.trade_name.icontains(query_str),
            Supplier.username.icontains(query_str),
            Supplier.phone.icontains(query_str),
            Supplier.sovereign_id.icontains(query_str)
        )
        db_query = db_query.filter(search_filter)

    # تطبيق فلاتر التصنيف
    if province: db_query = db_query.filter(Supplier.province == province)
    if district: db_query = db_query.filter(Supplier.district == district)
    if tier: db_query = db_query.filter(Supplier.tier == tier)
    if status: db_query = db_query.filter(Supplier.status == status)

    suppliers = db_query.order_by(Supplier.id.desc()).all()
    
    # استخدام to_dict الموحدة في الموديل لضمان دقة البيانات والعملات
    return jsonify([s.to_dict() for s in suppliers])

# --- 6. تفاصيل الكيان (للمودال الذكي) ---
@admin_bp.route('/api/suppliers/<int:sup_id>')
@admin_api_required
def api_get_supplier(sup_id):
    """ جلب بيانات المورد مع كتيبة الموظفين التابعة له """
    s = Supplier.query.get_or_404(sup_id)
    # نمرر include_staff لجلب العلاقة التي أضفناها في النموذج
    return jsonify(s.to_dict(include_staff=True))

# --- 7. إضافة وتعمد مورد جديد ---
@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if not is_admin_sovereign(): 
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        try:
            # التحقق من عدم تكرار اسم المستخدم
            if Supplier.query.filter_by(username=request.form.get('username')).first():
                raise Exception("اسم المستخدم مسجل مسبقاً في الترسانة")

            new_supplier = Supplier(
                username=request.form.get('username'),
                owner_name=request.form.get('owner_name'),
                trade_name=request.form.get('trade_name'),
                phone=request.form.get('phone'),
                province=request.form.get('province'),
                district=request.form.get('district'),
                tier=request.form.get('tier', 'مبتدئ'),
                status='active'
            )
            new_supplier.set_password(request.form.get('password', '123456'))
            
            db.session.add(new_supplier)
            db.session.flush() # للحصول على ID قبل الـ commit
            
            # نقش المعرف السيادي (SUP_MAH_...)
            new_supplier.mint_sovereign_id()
            
            db.session.commit()
            
            if is_ajax: 
                return jsonify({'status': 'success', 'message': 'تم تعميد المورد ومنحه الهوية الرقمية'})
            flash(f"تم إضافة {new_supplier.trade_name} للترسانة بنجاح", "success")
            return redirect(url_for('admin.manage_suppliers'))
            
        except Exception as e:
            db.session.rollback()
            if is_ajax: return jsonify({'status': 'error', 'message': str(e)}), 400
            flash(f"خطأ في البروتوكول: {str(e)}", "danger")

    return render_template('add_supplier.html')

# --- 8. تحديث الأرصدة والحالة (التحكم المالي) ---
@admin_bp.route('/api/supplier/<int:sup_id>/update-finance', methods=['POST'])
@admin_api_required
def update_supplier_finance(sup_id):
    """ تحديث أرصدة العملات الثلاث مباشرة من لوحة التحكم """
    supplier = Supplier.query.get_or_404(sup_id)
    data = request.get_json()
    
    try:
        supplier.balance_yer = data.get('balance_yer', supplier.balance_yer)
        supplier.balance_sar = data.get('balance_sar', supplier.balance_sar)
        supplier.balance_usd = data.get('balance_usd', supplier.balance_usd)
        supplier.status = data.get('status', supplier.status)
        
        db.session.commit()
        return jsonify({"status": "success", "message": "تم تحديث الخزينة بنجاح"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@admin_bp.route('/api/toggle-supplier-status/<int:sup_id>', methods=['POST'])
@admin_api_required
def toggle_supplier_status(sup_id):
    """ تبديل حالة الحساب (نشط/موقف) """
    supplier = Supplier.query.get_or_404(sup_id)
    supplier.status = 'suspended' if supplier.status == 'active' else 'active'
    db.session.commit()
    return jsonify({"status": "success", "new_status": supplier.status})

@admin.route('/supplier/<int:supplier_id>/profile')
def supplier_profile(supplier_id):
    # جلب بيانات المورد من القاعدة
    supplier = Supplier.query.get_or_forward_404(supplier_id)
    # فتح الملف الجديد الذي أنشأناه في مجلد suppliers
    return render_template('suppliers/supplier_profile.html', supplier=supplier)
    
# --- 9. إنهاء الجلسة السيادية ---
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("تم تأمين الخروج من مركز القيادة.", "info")
    return redirect(url_for('admin.login'))
