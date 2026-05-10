from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, logout_user, current_user
from datetime import datetime
from sqlalchemy import func
from . import admin_bp
from core import db # استيراد الجلسة للعمليات الحسابية

# استيراد النواة والترسانة الأمنية
from core.models import User, Supplier, Order, Product
from core.security import admin_required
from core.utils.archive_manager import archive_manager

# --- 1. مركز القيادة الإحصائي (Dashboard) ---
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required # استخدمنا الحارس الذي برمجناه في security.py
def admin_dashboard():
    # حساب الأرصدة الإجمالية من قاعدة البيانات مباشرة
    total_yer = db.session.query(func.sum(Supplier.balance_yer)).scalar() or 0.0
    total_sar = db.session.query(func.sum(Supplier.balance_sar)).scalar() or 0.0
    total_usd = db.session.query(func.sum(Supplier.balance_usd)).scalar() or 0.0

    stats = {
        'users_count': User.query.count(),
        'suppliers_count': Supplier.query.count(),
        'orders_count': Order.query.count() if Order else 0,
        'products_count': Product.query.count() if Product else 0,
        'total_yer': f"{total_yer:,.2f}", # تنسيق رقمي احترافي
        'total_sar': f"{total_sar:,.2f}",
        'total_usd': f"{total_usd:,.2f}",
        'now': datetime.now() # نرسله ككائن لتنسيقه داخل التمبلت
    }
    return render_template('dashboard.html', **stats)

# --- 2. إدارة الموردين (الواجهة والـ API) ---

@admin_bp.route('/manage-suppliers')
@admin_required
def manage_suppliers():
    return render_template('manage_suppliers.html')

@admin_bp.route('/add-supplier')
@admin_required
def add_supplier():
    """ صفحة تعميد مورد جديد """
    return render_template('add_supplier.html')

@admin_bp.route('/api/suppliers/search')
@admin_required
def api_search_suppliers():
    """ محرك البحث السيادي الذي يغذي sovereign_engine.js """
    query = request.args.get('q', '')
    province = request.args.get('province', '')
    status = request.args.get('status', '')

    search_query = Supplier.query
    if query:
        search_query = search_query.filter(Supplier.trade_name.contains(query))
    if province:
        search_query = search_query.filter(Supplier.province == province)
    if status:
        search_query = search_query.filter(Supplier.status == status)

    suppliers = search_query.all()
    return jsonify([sup.to_dict() for sup in suppliers])

@admin_bp.route('/api/supplier/<int:sup_id>')
@admin_required
def api_get_supplier(sup_id):
    """ جلب تفاصيل مورد واحد لفتح المودال """
    supplier = Supplier.query.get_or_404(sup_id)
    return jsonify(supplier.to_dict())

@admin_bp.route('/api/supplier/<int:sup_id>/archive', methods=['POST'])
@admin_required
def api_archive_supplier(sup_id):
    """ بوابة الأرشفة السيادية إلى GitHub """
    supplier = Supplier.query.get_or_404(sup_id)
    success, result = archive_manager.archive_supplier_data(supplier)
    if success:
        return jsonify({"success": True, "path": result})
    return jsonify({"success": False, "error": result}), 500

# --- 3. إنهاء الجلسة ---
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("تم تأمين الخروج من مركز القيادة بنجاح.", "info")
    return redirect(url_for('admin.login'))
