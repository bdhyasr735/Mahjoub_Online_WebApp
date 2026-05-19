# coding: utf-8
# 💳 محرك الحوكمة المالية والمسارات السيادية للمحافظ - منصة محجوب أونلاين 2026

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from apps import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import Wallet

# 🛡️ استدعاء آمن للموديل (WalletTransaction)
WalletTransaction = None
try:
    import apps.models.wallet_db as w_model
    if hasattr(w_model, 'WalletTransaction'):
        WalletTransaction = getattr(w_model, 'WalletTransaction')
    elif hasattr(w_model, 'WalletTransactions'):
        WalletTransaction = getattr(w_model, 'WalletTransactions')
except:
    pass

admin_wallet = Blueprint('admin_wallet', __name__, template_folder='templates')

@admin_wallet.route('/admin/wallet/overview', methods=['GET'])
@login_required
def overview():
    if current_user.role not in ['Owner', 'Admin']:
        return redirect(url_for('admin_dashboard.dashboard_home'))

    wallets = Wallet.query.all()
    totals = {
        'total_yer': sum(w.yer_available or 0 for w in wallets),
        'total_sar': sum(w.sar_available or 0 for w in wallets),
        'total_usd': sum(w.usd_available or 0 for w in wallets)
    }
    return render_template('admin/overview.html', wallets=wallets, totals=totals)

@admin_wallet.route('/admin/wallet/search_api', methods=['GET'])
@login_required
def search_api():
    search_query = request.args.get('query', '').strip()
    try:
        # الربط المرن (Outerjoin) لضمان ظهور المحفظة حتى لو لم يوجد مورد مرتبط حالياً
        query = db.session.query(Wallet, Supplier).outerjoin(Supplier, Wallet.supplier_id == Supplier.sovereign_id)
        
        if search_query:
            query = query.filter(
                (Supplier.trade_name.ilike(f'%{search_query}%')) |
                (Supplier.owner_name.ilike(f'%{search_query}%')) |
                (Wallet.wallet_code.ilike(f'%{search_query}%'))
            )
        
        results = []
        for w, s in query.all():
            results.append({
                "id": w.id,
                "wallet_code": w.wallet_code,
                "trade_name": s.trade_name if s else 'غير معرف',
                "sovereign_id": w.supplier_id or 'لا يوجد',
                "yer_balance": float(w.yer_available or 0),
                "sar_balance": float(w.sar_available or 0),
                "usd_balance": float(w.usd_available or 0)
            })
        return jsonify({"status": "success", "wallets": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@admin_wallet.route('/admin/wallet/adjust', methods=['POST'])
@login_required
def adjust_balance():
    if current_user.role != 'Owner':
        flash('هذا الإجراء يتطلب سلطة المالك السيادية.', 'danger')
        return redirect(url_for('admin_wallet.overview'))

    wallet_id = request.form.get('wallet_id')
    currency = request.form.get('currency')
    action_type = request.form.get('action_type')
    
    # منطق الخصم الثابت: إذا كان السحب، نخصم 30، وإلا نستخدم القيمة المدخلة
    try:
        raw_amount = float(request.form.get('amount', 0))
        amount = 30.0 if action_type == 'withdrawal' else raw_amount
    except:
        amount = 0

    if amount <= 0:
        flash('قيمة العملية غير صالحة.', 'warning')
        return redirect(url_for('admin_wallet.overview'))

    wallet = Wallet.query.get(wallet_id)
    if not wallet:
        flash('المحفظة غير موجودة.', 'danger')
        return redirect(url_for('admin_wallet.overview'))

    # التعديل الحوكمي
    if currency == 'YER':
        if action_type == 'deposit': wallet.yer_total += amount
        else: wallet.yer_withdrawn += amount
    elif currency == 'SAR':
        if action_type == 'deposit': wallet.sar_total += amount
        else: wallet.sar_withdrawn += amount
    elif currency == 'USD':
        if action_type == 'deposit': wallet.usd_total += amount
        else: wallet.usd_withdrawn += amount
    
    db.session.commit()
    flash(f'تم تنفيذ عملية {action_type} بنجاح.', 'success')
    return redirect(url_for('admin_wallet.overview'))
