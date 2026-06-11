from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from apps.extensions import db
from apps.models.vault_db import AdminVault, VaultTransaction

vault_bp = Blueprint('vault_bp', __name__, template_folder='templates')

@vault_bp.route('/admin/vault', methods=['GET'])
@login_required
def vault_dashboard():
    # جلب الخزينة (أو إنشاء واحدة إذا لم توجد)
    vault = AdminVault.query.first()
    if not vault:
        vault = AdminVault(balance_sar=0, balance_yer=0, balance_usd=0)
        db.session.add(vault)
        db.session.commit()
    
    transactions = VaultTransaction.query.order_by(VaultTransaction.created_at.desc()).limit(20).all()
    return render_template('admin/vault_dashboard.html', vault=vault, transactions=transactions)
