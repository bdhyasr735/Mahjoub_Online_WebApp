# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, abort
# تم تحديث الاستيراد ليتناسب مع الاسم الجديد VendorWallet
from apps.models.wallet_db import VendorWallet 
from apps.models.supplier_db import Supplier
from sqlalchemy import or_, cast, String
from flask_paginate import Pagination, get_page_parameter

# تعريف الـ Blueprint
wallet_app = Blueprint('wallet_app', __name__, template_folder='templates')

@wallet_app.route('/', methods=['GET'])
def dashboard():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not request.referrer or "mahjoub.online" not in request.referrer:
            abort(403)

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 15
    search = request.args.get('search', '')
    
    query = VendorWallet.query.join(Supplier)
    
    if search:
        query = query.filter(or_(
            Supplier.search_name.contains(search),
            Supplier.search_phone.contains(search),
            cast(VendorWallet.id, String).contains(search)
        ))
    
    total = query.count()
    wallets = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # تم تعديل الإحصائيات لتطابق الأعمدة الموجودة في كلاس VendorWallet فعلياً
    all_filtered = query.all()
    stats = {
        'count': total,
        'available': sum(float(w.balance_available) for w in all_filtered),
        'pending': sum(float(w.balance_pending) for w in all_filtered),
        'withdrawn': sum(float(w.total_withdrawn) for w in all_filtered)
    }
    
    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap5')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/partials/wallet_table_body.html', 
                               wallets=wallets, pagination=pagination, stats=stats)
    
    return render_template('admin/wallet_app.html', 
                           wallets=wallets, pagination=pagination, stats=stats)

@wallet_app.route('/search_suppliers', methods=['GET'])
def search_suppliers():
    term = request.args.get('term', '')
    suppliers = Supplier.query.filter(
        or_(Supplier.search_name.contains(term), Supplier.search_phone.contains(term))
    ).limit(10).all()
    results = [{'id': s.id, 'text': f"{s.trade_name} - {s.owner_phone}"} for s in suppliers]
    return jsonify({'results': results})

@wallet_app.route('/manage/<int:supplier_id>', methods=['GET'])
def manage_wallet(supplier_id):
    wallet = VendorWallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # ملاحظة: إذا كان كلاس WalletTransaction غير موجود، ستحتاج لتعريفه أو إزالته
    # من هنا ومن ملفات الاستيراد لتفادي خطأ ImportError
    # query = WalletTransaction.query.filter_by(wallet_id=wallet.id)
    
    return render_template('admin/view_wallet.html', wallet=wallet)
