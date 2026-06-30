from apps.models.admin_db import AdminUser
from apps.models.supplier_profile_db import SupplierProfile # أو الموديل الخاص بالموردين
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from sqlalchemy import func

@admin_dashboard.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    admin_required()
    
    # 1. إجمالي الموردين
    total_suppliers = SupplierProfile.query.count()
    
    # 2. الأرصدة (مثال لجمع الأرصدة من المحفظة)
    total_balance_sar = db.session.query(func.sum(SupplierWallet.balance_sar)).scalar() or 0
    
    # 3. آخر 10 عمليات
    recent_transactions = WalletTransaction.query.order_by(WalletTransaction.created_at.desc()).limit(10).all()
    
    context = {
        'total_suppliers': total_suppliers,
        'total_balance_sar': float(total_balance_sar),
        'recent_transactions': recent_transactions
    }
    
    return render_template('admin/dashboard.html', **context)
