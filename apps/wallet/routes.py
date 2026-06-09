# 📂 apps/wallet/routes.py
from flask import render_template, request, jsonify
from flask_login import login_required
from sqlalchemy import or_
from sqlalchemy.orm import joinedload # مهم جداً لجلب المحفظة مع المورد
from apps import db 
from apps.models.wallet_db import SupplierWallet as Wallet, WalletTransaction as Transaction
from apps.models.supplier_db import Supplier
from apps.wallet import wallet_app

@wallet_app.route('/get_suppliers_list')
@login_required
def get_suppliers_list():
    page = request.args.get('page', 1, type=int)
    # نستخدم joinedload لربط المحفظة فوراً وتجنب خطأ N+1
    suppliers = Supplier.query.options(joinedload(Supplier.wallet))\
                              .paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/suppliers_list.html', suppliers=suppliers)

@wallet_app.route('/search_suppliers')
@login_required
def search_suppliers():
    q = request.args.get('q', '')
    if not q: return jsonify({"results": []})
    
    # البحث في الحقول المفهرسة (غير المشفرة)
    suppliers = Supplier.query.filter(
        or_(
            Supplier.search_name.ilike(f'%{q}%'),
            Supplier.search_phone.ilike(f'%{q}%')
        )
    ).limit(10).all()
    
    # عرض الاسم المفكوك تشفيره
    results = [{"id": s.id, "text": f"{s.trade_name} - {s.owner_phone}"} for s in suppliers]
    return jsonify({"results": results})
