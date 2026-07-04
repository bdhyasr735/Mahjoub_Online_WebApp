# coding: utf-8
# 📂 apps/admin_dashboard/routes.py

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required

# 1. إنشاء الـ Blueprint
admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates'
)

# 2. مسار لوحة التحكم
@admin_dashboard.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """عرض لوحة تحكم النظام الرئيسية."""
    context = {
        "total_suppliers": 0,
        "total_balance_sar": 0.00,
        "total_balance_yer": 0.00,
        "total_balance_usd": 0.00,
        "recent_transactions": []
    }
    return render_template('admin/dashboard.html', **context)

# 3. مسار البحث الشامل (السيادي)
@admin_dashboard.route('/search', methods=['GET'])
@login_required
def search():
    """البحث في كافة أرجاء النظام."""
    # يتم استيراد النماذج هنا (Lazy Import) لحل مشكلة الدائرة المغلقة (Circular Import)
    from apps.models import Store, Product, Order 
    
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('admin_dashboard.dashboard'))

    # البحث باستخدام ilike ليكون غير حساس لحالة الأحرف
    search_term = f"%{query}%"
    
    results = {
        "stores": Store.query.filter(Store.name.ilike(search_term)).all(),
        "products": Product.query.filter(Product.name.ilike(search_term)).all(),
        "orders": Order.query.filter(Order.id.ilike(search_term)).all()
    }
    
    return render_template('admin/search_results.html', 
                           query=query, 
                           results=results)
