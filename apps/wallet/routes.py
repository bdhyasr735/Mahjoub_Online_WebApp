# 📂 apps/wallet/routes.py
from flask import render_template, request, jsonify
from flask_login import login_required
from sqlalchemy import func
from apps import db 

# استيراد الموديلات
from apps.models.wallet_db import SupplierWallet as Wallet, WalletTransaction as Transaction
from apps.models.supplier_db import Supplier

# استيراد الـ Blueprint
from apps.wallet import wallet_app

# 1. لوحة تحكم المحفظة (الداشبورد)
@wallet_app.route('/wallet_dashboard')
@login_required
def wallet_dashboard():
    # حساب الإحصائيات العامة للمحافظ
    stats = {
        "usd": db.session.query(func.sum(Wallet.balance_usd)).scalar() or 0,
        "sar": db.session.query(func.sum(Wallet.balance_sar)).scalar() or 0,
        "yer": db.session.query(func.sum(Wallet.balance_yer)).scalar() or 0,
        "count": Wallet.query.count()
    }
    # هذا الملف يحتوي على الهيكل الأساسي (Base Template)
    return render_template('admin/wallet_app.html', stats=stats)

# 2. جلب قائمة الموردين مع التصفح (Pagination)
# يُستدعى عبر AJAX ليتم حقنه في #suppliersTable
@wallet_app.route('/get_suppliers_list')
@login_required
def get_suppliers_list():
    page = request.args.get('page', 1, type=int)
    suppliers = Supplier.query.paginate(page=page, per_page=10, error_out=False)
    # ملاحظة: هذا الملف لا يجب أن يحتوي على {% extends %}
    return render_template('admin/suppliers_list.html', suppliers=suppliers)

# 3. عرض محفظة مورد معين (يُستدعى عبر AJAX)
# يُستدعى عبر AJAX ليتم حقنه في #walletDisplayArea
@wallet_app.route('/view/<int:supplier_id>')
@login_required
def view_wallet(supplier_id):
    page = request.args.get('page', 1, type=int)
    wallet = Wallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    
    transactions = Transaction.query.filter_by(wallet_id=wallet.id)\
        .order_by(Transaction.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
        
    # ملاحظة: هذا الملف لا يجب أن يحتوي على {% extends %}
    return render_template('admin/view_wallet.html', wallet=wallet, transactions=transactions)

# 4. دالة البحث المدمجة (Select2 AJAX)
@wallet_app.route('/search_suppliers')
@login_required
def search_suppliers():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"results": []})
    
    # البحث في الموردين بالاسم أو الهاتف
    suppliers = Supplier.query.filter(
        (Supplier.trade_name.ilike(f'%{query}%')) | 
        (Supplier.owner_phone.ilike(f'%{query}%'))
    ).limit(10).all()
    
    # تحويل النتائج لتنسيق Select2
    results = [{"id": s.id, "text": f"{s.trade_name} - {s.owner_phone}"} for s in suppliers]
    return jsonify({"results": results})
