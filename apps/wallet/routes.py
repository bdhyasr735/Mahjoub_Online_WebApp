# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required
from apps import db 
from apps.models.wallet_db import SupplierWallet
from apps.models.supplier_db import Supplier
from sqlalchemy import func
from apps.wallet import wallet_bp # استيراد البلوبرينت المعرف في __init__.py

@wallet_bp.route('/wallet_page')
@login_required
def wallet_home():
    """
    الدالة الرئيسية للفضاء المالي.
    تأكد أن الاسم هنا 'wallet_home' ليطابق url_for('wallet.wallet_home')
    """
    totals = db.session.query(
        func.sum(SupplierWallet.yer_total).label('total_yer'),
        func.sum(SupplierWallet.sar_total).label('total_sar'),
        func.sum(SupplierWallet.usd_total).label('total_usd')
    ).first()
    
    totals_dict = {
        'total_yer': totals.total_yer or 0,
        'total_sar': totals.total_sar or 0,
        'total_usd': totals.total_usd or 0
    }
    
    return render_template('admin/wallet_dashboard.html', totals=totals_dict)

@wallet_bp.route('/search_api')
@login_required
def search_api():
    query = request.args.get('query', '')
    filter_type = request.args.get('filter', 'all')
    
    wallets_query = db.session.query(SupplierWallet, Supplier).join(
        Supplier, SupplierWallet.supplier_id == Supplier.sovereign_id
    )
    
    if query:
        wallets_query = wallets_query.filter(
            (Supplier.trade_name.contains(query)) | 
            (SupplierWallet.wallet_code.contains(query))
        )
    
    if filter_type == 'active':
        wallets_query = wallets_query.filter(SupplierWallet.status == 'نشطة')
    elif filter_type == 'idle':
        wallets_query = wallets_query.filter(SupplierWallet.status != 'نشطة')
        
    results = wallets_query.all()
    
    wallets_data = []
    for w, s in results:
        wallets_data.append({
            'id': w.id,
            'wallet_code': w.wallet_code,
            'trade_name': s.trade_name,
            'sovereign_id': s.sovereign_id,
            'yer_balance': float(w.yer_total or 0),
            'sar_balance': float(w.sar_total or 0),
            'usd_balance': float(w.usd_total or 0)
        })
        
    return jsonify({'wallets': wallets_data})

@wallet_bp.route('/adjust', methods=['POST'])
@login_required
def adjust_balance():
    wallet_id = request.form.get('wallet_id')
    currency = request.form.get('currency')
    action_type = request.form.get('action_type')
    amount = float(request.form.get('amount', 0))
    
    wallet = SupplierWallet.query.get_or_404(wallet_id)
    
    field_map = {'YER': 'yer_total', 'SAR': 'sar_total', 'USD': 'usd_total'}
    
    field = field_map.get(currency)
    if field:
        current_val = float(getattr(wallet, field) or 0)
        if action_type == 'deposit':
            setattr(wallet, field, current_val + amount)
        else:
            setattr(wallet, field, current_val - amount)
            
        db.session.commit()
        flash(f"تم تنفيذ العملية بنجاح على محفظة {wallet.wallet_code}", "success")
    
    # إعادة التوجيه إلى المسار المصحح
    return redirect(url_for('wallet.wallet_home'))
