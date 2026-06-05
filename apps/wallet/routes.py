# 📂 apps/wallet/routes.py - المحرك المالي السيادي (النسخة النهائية)
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from sqlalchemy import func
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet, WalletTransaction

# إنشاء البلوبيرنت (المصنع المالي)
wallet_bp = Blueprint('wallet_app', __name__)

@wallet_bp.route('/dashboard')
@login_required
def dashboard():
    """
    محرك لوحة التحكم: يحسب أرصدة مليون محفظة لحظياً بـ func.sum
    """
    # استعلام ذكي وسريع (SQL-Side Aggregation)
    # لا نقوم بجمع البيانات في بايثون، بل نطلب من قاعدة البيانات الحساب مباشرة
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
    محرك عرض المحفظة: يستدعي بيانات مورد واحد فقط (Direct Fetch)
    """
    # 1. جلب بيانات المورد (معالجة أخطاء 404 في حال كان المعرف خاطئاً)
    supplier = Supplier.query.get_or_404(supplier_id)
    
    # 2. جلب المحفظة المرتبطة بالمورد
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
    
    # 3. جلب آخر 50 حركة مالية فقط (Pagination/Limit)
    # هذا يمنع انهيار الواجهة في حال كان للمورد آلاف الحركات
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
    محرك API للتحديث اللحظي للأرصدة (Live Dashboard)
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
