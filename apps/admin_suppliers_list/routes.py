# coding: utf-8
# 📂 apps/admin_suppliers_list/routes.py

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet

suppliers_bp = Blueprint('suppliers_bp', __name__, template_folder='templates')

@suppliers_bp.route('/list')
@login_required
def list_suppliers():
    """
    عرض قائمة الموردين مع دمج بياناتهم المالية.
    تم استخدام نظام الجلب المباشر لضمان دقة ظهور الأرصدة.
    """
    try:
        # جلب الموردين
        suppliers = Supplier.query.all()
        suppliers_data = []
        
        for s in suppliers:
            # جلب المحفظة المرتبطة بالمورد مباشرة
            wallet = SupplierWallet.query.filter_by(supplier_id=s.id).first()
            suppliers_data.append({
                'supplier': s,
                'balance_usd': wallet.balance_usd if wallet else 0,
                'balance_yer': wallet.balance_yer if wallet else 0,
                'balance_sar': wallet.balance_sar if wallet else 0
            })
        
        return render_template(
            'admin_suppliers_list/admin_suppliers_list.html', 
            suppliers_data=suppliers_data
        )
    except Exception as e:
        flash(f"خطأ في عرض الخزينة: {str(e)}", "error")
        return redirect(url_for('admin_dashboard.index'))

@suppliers_bp.route('/settle/<int:supplier_id>/<string:currency>')
@login_required
def settle_supplier_funds(supplier_id, currency):
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    if not wallet:
        flash("خطأ: المحفظة غير موجودة.", "error")
        return redirect(url_for('suppliers_bp.list_suppliers'))

    # التصفية السيادية
    if currency == 'USD': wallet.balance_usd = 0
    elif currency == 'YER': wallet.balance_yer = 0
    elif currency == 'SAR': wallet.balance_sar = 0
    
    db.session.commit()
    flash(f"✅ تمت التصفية لعملة {currency}", "success")
    return redirect(url_for('suppliers_bp.list_suppliers'))
