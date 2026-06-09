# 📂 apps/wallet/routes.py
from flask import render_template, request, jsonify
from flask_login import login_required
from sqlalchemy import or_, func
from apps import db 
from apps.models.wallet_db import SupplierWallet as Wallet, WalletTransaction as Transaction
from apps.models.supplier_db import Supplier
from apps.wallet import wallet_app

# 1. مسار الداشبورد: عرض الإحصائيات والقالب الأساسي
@wallet_app.route('/wallet_dashboard')
@login_required
def wallet_dashboard():
    stats = {
        "usd": db.session.query(func.sum(Wallet.balance_usd)).scalar() or 0,
        "sar": db.session.query(func.sum(Wallet.balance_sar)).scalar() or 0,
        "yer": db.session.query(func.sum(Wallet.balance_yer)).scalar() or 0,
        "count": Wallet.query.count()
    }
    return render_template('admin/wallet_app.html', stats=stats)

# 2. مسار البحث الذكي: جلب الموردين لـ Select2
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

# 3. مسار جلب قائمة الموردين للجدول
@wallet_app.route('/get_suppliers_list')
@login_required
def get_suppliers_list():
    page = request.args.get('page', 1, type=int)
    # جلب الموردين مع الترقيم
    suppliers = Supplier.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/suppliers_list.html', suppliers=suppliers)

# 4. مسار عرض كشف المحفظة (الربط اليدوي للمورد)
@wallet_app.route('/view/<int:supplier_id>')
@login_required
def view_wallet(supplier_id):
    page = request.args.get('page', 1, type=int)
    
    # أ. جلب بيانات المحفظة
    wallet = Wallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    
    # ب. جلب بيانات المورد يدوياً (بدون تعديل الموديل)
    supplier_info = Supplier.query.get(supplier_id)
    
    # ج. جلب الحركات المالية المربوطة بالمحفظة
    transactions = Transaction.query.filter_by(wallet_id=wallet.id)\
        .order_by(Transaction.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    # د. إرجاع القالب مع كافة المتغيرات المطلوبة
    return render_template('admin/view_wallet.html', 
                           wallet=wallet, 
                           supplier=supplier_info, 
                           transactions=transactions,
                           is_mourning_period=False) # يمكنك ربطها بمتغير إعدادات النظام
