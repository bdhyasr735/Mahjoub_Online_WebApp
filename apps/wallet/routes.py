from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from apps import db
from apps.models import Wallet, Supplier
from apps.models.settlements_db import AdminSettlement

blueprint = Blueprint('wallet', __name__, url_prefix='/wallet')

@blueprint.route('/management', methods=['GET'])
@login_required
def display_management_table():
    search_query = request.args.get('search_query')
    wallet = None
    wallet_settlements = []
    
    # إحصائيات النظام (استخدام scalar للجمع الآمن)
    total_wallets_count = Wallet.query.count()
    total_yer_system = db.session.query(db.func.sum(Wallet.yer_available)).scalar() or 0
    total_sar_system = db.session.query(db.func.sum(Wallet.sar_available)).scalar() or 0
    
    if search_query:
        # بحث مرن ومحكم
        wallet = Wallet.query.join(Supplier).filter(
            (Wallet.wallet_code.ilike(f'%{search_query}%')) |
            (Wallet.supplier_id.ilike(f'%{search_query}%')) |
            (Supplier.name.ilike(f'%{search_query}%')) |
            (Supplier.owner_name.ilike(f'%{search_query}%'))
        ).first()
        
        if wallet:
            # جلب السجلات من الجدول المخصص الجديد
            wallet_settlements = AdminSettlement.query.filter_by(
                wallet_id=wallet.id
            ).order_by(AdminSettlement.created_at.desc()).all()
    
    return render_template(
        'admin/settlement_and_withdrawal.html',
        wallet=wallet,
        wallet_settlements=wallet_settlements,
        total_wallets_count=total_wallets_count,
        total_yer_system=total_yer_system,
        total_sar_system=total_sar_system,
        current_search=search_query
    )

# ملاحظة: تأكد من أنك قمت بتعريف المسار في الـ Blueprint الخاص بك
