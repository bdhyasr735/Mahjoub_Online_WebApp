# coding: utf-8
# 📂 apps/suppliers_wallet/routes.py

from flask import Blueprint, render_template, abort, request, session
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_parameter
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.api.sync_engine import SyncEngine
from datetime import datetime, timedelta
from sqlalchemy import func

# تم تعريف الـ Blueprint باسم فريد لضمان عدم التعارض
supplier_wallet_bp = Blueprint('supplier_wallet', __name__, template_folder='templates')

@supplier_wallet_bp.route('/my-wallet', methods=['GET'])
@login_required
def view_my_wallet():
    # 1. تحديد الـ s_id بمرونة وأمان
    user_type = session.get('user_type')
    s_id = None
    
    if user_type == 'supplier':
        s_id = current_user.id
    elif user_type == 'staff':
        s_id = getattr(current_user, 'supplier_id', None)
    else:
        s_id = request.args.get('supplier_id')
        
    if not s_id:
        abort(400, description="يجب تحديد معرف المورد لعرض المحفظة.")
    
    # 2. جلب محفظة المورد (استخدام try-except للتعامل مع أخطاء قواعد البيانات)
    try:
        wallet = SupplierWallet.query.filter_by(supplier_id=int(s_id)).first()
    except ValueError:
        abort(400, description="معرف المورد غير صالح.")
        
    if not wallet:
        abort(404, description="لم يتم العثور على محفظة مرتبطة بهذا المورد.")

    # 3. الفلاتر الأساسية
    currency = request.args.get('currency', 'SAR')
    filter_type = request.args.get('filter_type', 'all')
    search = request.args.get('search', '').strip()
    
    query = WalletTransaction.query.filter_by(wallet_id=wallet.id, currency=currency)

    # 4. الفلترة الزمنية
    now = datetime.utcnow()
    if filter_type == 'day':
        query = query.filter(WalletTransaction.created_at >= now.date())
    elif filter_type == 'week':
        query = query.filter(WalletTransaction.created_at >= (now - timedelta(days=7)))
    elif filter_type == 'month':
        query = query.filter(WalletTransaction.created_at >= (now - timedelta(days=30)))
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date: query = query.filter(WalletTransaction.created_at >= start_date)
    if end_date: query = query.filter(WalletTransaction.created_at <= end_date)

    # 5. البحث المرن
    if search:
        query = query.filter(
            (WalletTransaction.voucher_number.ilike(f'%{search}%')) | 
            (WalletTransaction.description.ilike(f'%{search}%'))
        )

    # 6. حساب الإجماليات
    stats = query.with_entities(
        func.sum(WalletTransaction.amount).filter(
            WalletTransaction.trans_type.in_(['credit', 'adjustment_credit', 'sale_revenue'])
        ).label('total_credit'),
        func.sum(WalletTransaction.amount).filter(
            WalletTransaction.trans_type.in_(['withdrawal', 'adjustment_debit'])
        ).label('total_debit')
    ).first()
    
    total_credit = stats.total_credit or 0
    total_debit = stats.total_debit or 0
    
    # منطق التدقيق للمدير فقط
    wallet_imbalance = None
    if getattr(current_user, 'is_admin', False):
        calculated_balance = total_credit - total_debit
        if abs(float(wallet.balance or 0) - float(calculated_balance)) > 0.01:
            wallet_imbalance = calculated_balance

    # 7. الترقيم
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 20
    total_records = query.count()
    pagination = Pagination(page=page, total=total_records, per_page=per_page, css_framework='bootstrap5')
    
    transactions = query.order_by(WalletTransaction.created_at.desc())\
                        .offset((page - 1) * per_page)\
                        .limit(per_page).all()

    # 8. استجابة (مع دعم الـ AJAX)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('supplier_wallet/_table_partial.html', 
                               transactions=transactions, 
                               total_debit=total_debit, 
                               total_credit=total_credit)

    return render_template('supplier_wallet/supplier_wallet.html', 
                           wallet=wallet, 
                           transactions=transactions, 
                           pagination=pagination,
                           total_debit=total_debit, 
                           total_credit=total_credit,
                           wallet_imbalance=wallet_imbalance)

@supplier_wallet_bp.route('/test-sync', methods=['GET'])
@login_required
def test_sync():
    if not getattr(current_user, 'is_admin', False): 
        abort(403)
    if SyncEngine.fetch_and_sync_order():
        return "✅ تم تنفيذ المزامنة بنجاح."
    return "❌ فشل عملية المزامنة."
