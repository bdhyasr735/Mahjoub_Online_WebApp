# coding: utf-8
# 💳 محرك الحوكمة المالية والمسارات السيادية للمحافظ اللحظية - منصة محجوب أونلاين 2026

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from apps import db
from apps.models.supplier_db import Supplier

try:
    from apps.models.wallet_db import Wallet
except ImportError:
    class Wallet(object):
        query = None

WalletTransaction = None
try:
    import apps.models.wallet_db as w_model
    if hasattr(w_model, 'WalletTransaction'):
        WalletTransaction = getattr(w_model, 'WalletTransaction')
    elif hasattr(w_model, 'WalletTransactions'):
        WalletTransaction = getattr(w_model, 'WalletTransactions')
except Exception:
    pass

admin_wallet = Blueprint('admin_wallet', __name__, template_folder='templates')

@admin_wallet.route('/admin/wallet/overview', methods=['GET'])
@login_required
def overview():
    if current_user.role not in ['Owner', 'Admin']:
        flash('غير مسموح لك بامتلاك صلاحية دخول الفضاء المالي.', 'danger')
        return redirect(url_for('admin_dashboard.dashboard_home'))

    # 1. حساب الإجماليات بشكل منفصل لتجنب أي تعارض
    totals = {'total_yer': 0, 'total_sar': 0, 'total_usd': 0}
    try:
        if Wallet.query is not None:
            res = db.session.query(
                func.sum(Wallet.yer_balance),
                func.sum(Wallet.sar_balance),
                func.sum(Wallet.usd_balance)
            ).first()
            if res:
                totals = {'total_yer': res[0] or 0, 'total_sar': res[1] or 0, 'total_usd': res[2] or 0}
    except Exception as e:
        print(f"تنبيه: تعذر حساب الإجماليات - {e}")

    # 2. جلب المحافظ بـ Outer Join لضمان عدم توقف النظام حتى لو بيانات المورد ناقصة
    wallets = []
    try:
        if Wallet.query is not None:
            wallets = Wallet.query.outerjoin(Supplier, Wallet.supplier_id == Supplier.id).all()
    except Exception as e:
        print(f"تنبيه: تعذر جلب المحافظ - {e}")

    return render_template('admin/overview.html', wallets=wallets, totals=totals)


@admin_wallet.route('/admin/wallet/search_api', methods=['GET'])
@login_required
def search_api():
    if current_user.role not in ['Owner', 'Admin']:
        return jsonify({"status": "error", "message": "صلاحية مرفوضة"}), 403

    search_query = request.args.get('query', '').strip()
    results = []

    if Wallet.query is None:
        return jsonify({"status": "success", "wallets": []})

    try:
        query = Wallet.query.outerjoin(Supplier, Wallet.supplier_id == Supplier.id)
        if search_query:
            query = query.filter(
                (Supplier.trade_name.like(f'%{search_query}%')) |
                (Supplier.sovereign_id.like(f'%{search_query}%')) |
                (Wallet.wallet_code.like(f'%{search_query}%'))
            )
        
        for w in query.all():
            results.append({
                "id": w.id,
                "wallet_code": w.wallet_code,
                "trade_name": w.supplier.trade_name if w.supplier else 'غير معرف',
                "sovereign_id": w.supplier.sovereign_id if w.supplier else '-',
                "yer_balance": float(getattr(w, 'yer_balance', 0.0)),
                "sar_balance": float(getattr(w, 'sar_balance', 0.0)),
                "usd_balance": float(getattr(w, 'usd_balance', 0.0))
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "success", "wallets": results})


@admin_wallet.route('/admin/wallet/adjust', methods=['POST'])
@login_required
def adjust_balance():
    if current_user.role != 'Owner':
        flash('هذا الإجراء يتطلب سلطة المالك.', 'danger')
        return redirect(url_for('admin_wallet.overview'))

    wallet_id = request.form.get('wallet_id')
    currency = request.form.get('currency')  
    action_type = request.form.get('action_type')  
    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        amount = 0

    if amount <= 0:
        flash('يجب إدخال مبلغ صحيح.', 'warning')
        return redirect(url_for('admin_wallet.overview'))

    try:
        wallet = Wallet.query.get(wallet_id)
        if not wallet:
            flash('المحفظة غير موجودة.', 'danger')
            return redirect(url_for('admin_wallet.overview'))

        if currency == 'YER':
            wallet.yer_balance = (wallet.yer_balance + amount) if action_type == 'deposit' else (wallet.yer_balance - amount)
        elif currency == 'SAR':
            wallet.sar_balance = (wallet.sar_balance + amount) if action_type == 'deposit' else (wallet.sar_balance - amount)
        elif currency == 'USD':
            wallet.usd_balance = (wallet.usd_balance + amount) if action_type == 'deposit' else (wallet.usd_balance - amount)
        
        if WalletTransaction:
            db.session.add(WalletTransaction(
                wallet_id=wallet.id,
                transaction_type=action_type,
                currency=currency,
                amount=amount,
                description=f"تعديل إداري سيادي: {action_type}"
            ))

        db.session.commit()
        flash(f'تم تنفيذ الفرمان المالي للمحفظة {wallet.wallet_code}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'عطل في التنفيذ: {e}', 'danger')

    return redirect(url_for('admin_wallet.overview'))
