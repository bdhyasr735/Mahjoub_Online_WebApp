# 📂 apps/wallet/routes.py - المحرك المالي الاحترافي
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from sqlalchemy import func
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet, WalletTransaction

# تعريف المحرك (يجب أن يطابق الاسم المستخدم في __init__.py)
wallet_app = Blueprint('wallet_app', __name__)

@wallet_app.route('/view/<int:supplier_id>')
@login_required
def view_wallet(supplier_id):
    # 1. جلب بيانات المورد والمحفظة الخاصة به
    supplier = Supplier.query.get_or_404(supplier_id)
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
    
    # في حال عدم وجود محفظة للمورد، ننشئها أو نرسل قيمة فارغة
    if not wallet:
        return "هذا المورد لا يمتلك محفظة حالياً.", 404

    # 2. تحديد رقم الصفحة للترقيم (Pagination)
    page = request.args.get('page', 1, type=int)
    
    # 3. جلب العمليات المالية بنظام الترقيم (20 عملية في كل صفحة)
    pagination = WalletTransaction.query.filter_by(wallet_id=wallet.id)\
        .order_by(WalletTransaction.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    transactions = pagination.items
    
    # 4. إرسال البيانات إلى ملف التفاصيل (Fragment)
    return render_template('admin/wallet_app_detail.html', 
                           supplier=supplier, 
                           wallet=wallet, 
                           transactions=transactions,
                           pagination=pagination)

@wallet_app.route('/api/stats')
@login_required
def get_stats():
    # 5. حساب إجمالي أرصدة النظام (لصناديق الإحصائيات في الصفحة الرئيسية)
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
