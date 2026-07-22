# coding: utf-8
# 📂 apps/suppliers_dashboard/settings_routes.py

from flask import Blueprint, render_template, abort, session, request, flash, redirect, url_for
from flask_login import login_required, current_user

from apps.models import db, Supplier, SupplierWallet
from apps.models.supplier_profile_db import SupplierProfile

settings_bp = Blueprint(
    'suppliers_settings',
    __name__,
    template_folder='templates'
)


def get_supplier_context():
    user_type = session.get('user_type')
    if user_type not in ['supplier', 'staff']:
        return None
    supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id
    supplier = db.session.get(Supplier, supplier_id)
    if supplier:
        wallet = db.session.execute(
            db.select(SupplierWallet).filter_by(supplier_id=supplier.id)
        ).unique().scalar_one_or_none()
        supplier.wallet = wallet
    return supplier


@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    supplier = get_supplier_context()
    if not supplier:
        return redirect('/supplier/login')
    if request.method == 'POST':
        try:
            supplier.trade_name = request.form.get('trade_name', supplier.trade_name)
            supplier.owner_name = request.form.get('owner_name', supplier.owner_name)
            new_phone = request.form.get('phone', '')
            if new_phone and new_phone != supplier.phone:
                supplier.phone = new_phone
            profile = getattr(supplier, 'supplier_profile', None)
            if not profile:
                profile = SupplierProfile(supplier_id=supplier.id)
                db.session.add(profile)
            profile.email = request.form.get('email', '')
            profile.address = request.form.get('address', '')
            profile.description = request.form.get('description', '')
            db.session.commit()
            flash('✅ تم تحديث البيانات بنجاح', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'❌ حدث خطأ: {str(e)}', 'danger')
        return redirect(url_for('suppliers_settings.settings'))
    return render_template('suppliers/settings.html', supplier=supplier)
