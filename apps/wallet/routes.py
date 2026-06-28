# coding: utf-8
# 📂 apps/wallet/routes.py

from flask import Blueprint, render_template, request
from flask_login import login_required
from apps.models.wallet_db import SupplierWallet
from apps.models.supplier_db import Supplier
from apps.extensions import db
from sqlalchemy import or_

# تعريف البلوبرينت
wallet_bp = Blueprint(
    'wallet_app', 
    __name__, 
    template_folder='templates'
)

@wallet_bp.route('/admin/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    لوحة تحكم المحافظ: تدعم البحث، التصفح، والطلبات الجزئية (Ajax)
    """
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)

    # بناء استعلام البحث
    query = SupplierWallet.query.join(Supplier, SupplierWallet.supplier_id == Supplier.id)
    
    if search:
        query = query.filter(or_(
            Supplier.trade_name.ilike(f'%{search}%'),
            SupplierWallet.wallet_code.ilike(f'%{search}%'),
            Supplier.search_phone.ilike(f'%{search}%')
        ))

    # التصفح (20 عنصراً لكل صفحة)
    wallets = query.paginate(page=page, per_page=20, error_out=False)
    
    # حساب الإحصائيات العامة
    stats = {
        'count': SupplierWallet.query.count(),
        'sar': db.session.query(db.func.sum(SupplierWallet.balance_sar)).scalar() or 0,
        'yer': db.session.query(db.func.sum(SupplierWallet.balance_yer)).scalar() or 0,
        'usd': db.session.query(db.func.sum(SupplierWallet.balance_usd)).scalar() or 0
    }

    # التحقق مما إذا كان الطلب Ajax لتحديث الجدول فقط
    # تم تحديث المسار هنا ليتوافق مع المسار الجديد: admin/partials/wallet_table_body.html
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/partials/wallet_table_body.html', 
                               wallets=wallets.items, 
                               pagination=wallets)

    # الطلب العادي (تحميل الصفحة كاملة)
    return render_template('admin/wallet_app.html', 
                           wallets=wallets.items, 
                           stats=stats, 
                           pagination=wallets)

@wallet_bp.route('/admin/manage/<int:supplier_id>', methods=['GET'])
@login_required
def manage_wallet(supplier_id):
    """
    عرض تفاصيل محفظة مورد محدد
    """
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    return render_template('admin/view_wallet.html', wallet=wallet)
