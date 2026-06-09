from flask import render_template, request, jsonify
from flask_login import login_required
from sqlalchemy import func
from apps import db 
from apps.models.wallet_db import SupplierWallet as Wallet, WalletTransaction as Transaction
from apps.models.supplier_db import Supplier
from apps.wallet import wallet_app

@wallet_app.route('/wallet_dashboard')
@login_required
def wallet_dashboard():
    stats = {
        "usd": db.session.query(func.sum(Wallet.balance_usd)).scalar() or 0,
        "sar": db.session.query(func.sum(Wallet.balance_sar)).scalar() or 0,
        "yer": db.session.query(func.sum(Wallet.balance_# 📂 apps/wallet/routes.py
from flask import render_template, request, jsonify
from flask_login import login_required
from sqlalchemy import or_, func
from apps import db 
from apps.models.wallet_db import SupplierWallet as Wallet, WalletTransaction as Transaction
from apps.models.supplier_db import Supplier
from apps.wallet import wallet_app

# 1. مسار الداشبورد: المخطط الكامل (الجدول + الإحصائيات)
@wallet_app.route('/wallet_dashboard')
@login_required
def wallet_dashboard():
    # حساب الإحصائيات العامة
    stats = {
        "usd": db.session.query(func.sum(Wallet.balance_usd)).scalar() or 0,
        "sar": db.session.query(func.sum(Wallet.balance_sar)).scalar() or 0,
        "yer": db.session.query(func.sum(Wallet.balance_yer)).scalar() or 0,
        "count": Wallet.query.count()
    }
    
    # جلب جميع الموردين لعرضهم في مخطط الأعمدة (الجدول الثابت)
    # ملاحظة: إذا كان عدد الموردين كبيراً جداً، يُفضل استخدام الـ Pagination
    all_suppliers = Supplier.query.all()
    
    return render_template('admin/wallet_app.html', stats=stats, suppliers=all_suppliers)

# 2. مسار البحث الذكي (يغذي Select2)
@wallet_app.route('/search_suppliers')
@login_required
def search_suppliers():
    q = request.args.get('q', '')
    suppliers = Supplier.query.filter(
        or_(
            Supplier.trade_name.contains(q),
            Supplier.owner_phone.contains(q)
        )
    ).limit(10).all()
    
    results = [{"id": s.id, "text": f"{s.trade_name} - {s.owner_phone}"} for s in suppliers]
    return jsonify({"results": results})

# 3. مسار عرض كشف المحفظة (يغذي منطقة العرض الديناميكي #walletDisplayArea)
@wallet_app.route('/view/<int:supplier_id>')
@login_required
def view_wallet(supplier_id):
    page = request.args.get('page', 1, type=int)
    
    # جلب المحفظة
    wallet = Wallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    
    # جلب بيانات المورد
    supplier_info = Supplier.query.get(supplier_id)
    
    # جلب الحركات المالية الخاصة بالمحفظة
    transactions = Transaction.query.filter_by(wallet_id=wallet.id)\
        .order_by(Transaction.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    # إرجاع القالب الفرعي (الحركة التفصيلية)
    return render_template('admin/view_wallet.html', 
                           wallet=wallet, 
                           supplier=supplier_info, 
                           transactions=transactions,
                           is_mourning_period=False)yer)).scalar() or 0,
        "count": Wallet.query.count()
    }
    return render_template('admin/wallet_app.html', stats=stats)

@wallet_app.route('/get_suppliers_list')
@login_required
def get_suppliers_list():
    page = request.args.get('page', 1, type=int)
    suppliers = Supplier.query.paginate(page=page, per_page=10, error_out=False)
    # إرجاع القالب الفرعي للجدول فقط
    return render_template('admin/suppliers_list.html', suppliers=suppliers)

@wallet_app.route('/view/<int:supplier_id>')
@login_required
def view_wallet(supplier_id):
    page = request.args.get('page', 1, type=int)
    wallet = Wallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    supplier = Supplier.query.get(supplier_id)
    transactions = Transaction.query.filter_by(wallet_id=wallet.id).order_by(Transaction.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/view_wallet.html', wallet=wallet, supplier=supplier, transactions=transactions)
