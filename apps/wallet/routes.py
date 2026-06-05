# 📂 apps/wallet/routes.py - المحرك المالي السيادي
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from sqlalchemy import func
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet, WalletTransaction

# إنشاء البلوبيرنت (المصنع)
wallet_bp = Blueprint('wallet_app', __name__)

@wallet_bp.route('/dashboard')
@login_required
def dashboard():
    """
    محرك لوحة التحكم: يعرض الإحصائيات الشاملة للمنصة (بالعملات الثلاث)
    """
    # استعلام ذكي وسريع لحساب الإجماليات من المليون محفظة
    totals = db.session.query(
        func.sum(SupplierWallet.balance_sar),
        func.sum(SupplierWallet.balance_yer),
        func.sum(SupplierWallet.balance_usd)
    ).first()
    
    return render_template('admin/wallet_dashboard.html', 
                           total_system_sar=totals[0] or 0,
                           total_system_yer=totals[1] or 0,
                           total_system_usd=totals[2] or 0)

@wallet_bp.route('/view/<int:supplier_id>')
@login_required
def view_wallet(supplier_id):
    """
    محرك عرض محفظة المورد: يجمع بين هوية المورد، رصيده، وسجل عملياته
    """
    # 1. جلب المورد
    supplier = Supplier.query.get_or_404(supplier_id)
    
    # 2. جلب المحفظة المرتبطة
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
    
    # 3. جلب سجل الحركات (آخر 50 عملية لضمان السرعة)
    transactions = []
    if wallet:
        transactions = WalletTransaction.query.filter_by(wallet_id=wallet.id)\
                        .order_by(WalletTransaction.created_at.desc())\
                        .limit(50).all()
    
    return render_template('admin/wallet_app.html', 
                           supplier=supplier, 
                           wallet=wallet, 
                           transactions=transactions)

@wallet_bp.route('/api/stats')
@login_required
def get_stats():
    """
    محرك API لتحديث الإحصائيات حياً (Live Updates)
    """
    totals = db.session.query(
        func.sum(SupplierWallet.balance_sar),
        func.sum(SupplierWallet.balance_yer),
        func.sum(SupplierWallet.balance_usd)
    ).first()
    
    return jsonify({
        'sar': float(totals[0] or 0),
        'yer': float(totals[1] or 0),
        'usd': float(totals[2] or 0)
    })
