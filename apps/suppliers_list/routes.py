# coding: utf-8
# 📂 apps/suppliers_list/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy.orm import joinedload
from apps.models.supplier_db import Supplier
from apps.models.supplier_profile_db import SupplierProfile
from apps.extensions import db
from apps.utils.security import decrypt_data 

supplier_bp = Blueprint('supplier_app', __name__, template_folder='templates')

@supplier_bp.route('/list', methods=['GET'])
@login_required
def list_suppliers():
    # استقبال المعاملات
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    gov = request.args.get('gov', '').strip()
    rank = request.args.get('rank', '').strip()

    # بناء الاستعلام مع تحميل استباقي للعلاقات لضمان السرعة
    query = Supplier.query.options(
        joinedload(Supplier.supplier_profile),
        joinedload(Supplier.staff_members)
    )

    # تطبيق الفلاتر
    if search:
        query = query.filter(Supplier.trade_name.ilike(f'%{search}%'))
    if gov:
        query = query.join(SupplierProfile).filter(SupplierProfile.governorate == gov)
    if rank:
        query = query.filter(Supplier.rank == rank)

    # الترقيم (20 عنصر في الصفحة)
    pagination = query.order_by(Supplier.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    # فك تشفير البيانات الحساسة للعرض
    for s in pagination.items:
        if s.phone_primary:
            s.decrypted_phone = decrypt_data(s.phone_primary)
        if s.supplier_profile and hasattr(s.supplier_profile, '_bank_account_enc') and s.supplier_profile._bank_account_enc:
            s.supplier_profile.decrypted_bank = decrypt_data(s.supplier_profile._bank_account_enc)

    return render_template(
        'suppliers_list/suppliers_list.html',
        suppliers=pagination.items,
        pagination=pagination,
        search=search,
        gov=gov,
        rank=rank
    )

@supplier_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    if request.method == 'POST':
        try:
            # تحديث البيانات الأساسية للمورد
            supplier.trade_name = request.form.get('trade_name')
            supplier.rank = request.form.get('rank')
            supplier.status = request.form.get('status')
            
            # تحديث البيانات التفصيلية في البروفايل
            if supplier.supplier_profile:
                supplier.supplier_profile.governorate = request.form.get('governorate')
                supplier.supplier_profile.email = request.form.get('email')
                supplier.supplier_profile.city = request.form.get('city')
                supplier.supplier_profile.district = request.form.get('district')
            
            db.session.commit()
            flash('تم حفظ التعديلات بنجاح', 'success')
            return redirect(url_for('supplier_app.list_suppliers'))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء الحفظ: {str(e)}', 'danger')
            
    return render_template('suppliers_list/edit_supplier.html', supplier=supplier)
