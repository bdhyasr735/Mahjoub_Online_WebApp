# coding: utf-8
from flask import Blueprint, render_template, request, jsonify
from apps.models.wallet_db import SupplierWallet
from apps.models.supplier_db import Supplier
from sqlalchemy import or_
from flask_paginate import Pagination, get_page_parameter

# تعريف الـ Blueprint
wallet_app = Blueprint('wallet_app', __name__, template_folder='templates')

@wallet_app.route('/wallet', methods=['GET'])
def dashboard():
    # 1. إعداد متغيرات الترقيم
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 15
    search = request.args.get('search', '')
    
    # 2. بناء الاستعلام مع ربط جدول الموردين للوصول للحقول المشفرة
    # نستخدم join لضمان إمكانية الفلترة باسم المورد (المشفر)
    query = SupplierWallet.query.join(Supplier)
    
    if search:
        query = query.filter(or_(
            Supplier.search_name.contains(search),      # البحث في حقل البحث السريع (المفكوك)
            Supplier.search_phone.contains(search),     # البحث في رقم الهاتف السريع
            SupplierWallet.id.contains(search)
        ))
    
    # 3. حساب الإجمالي وجلب البيانات للصفحة الحالية
    total = query.count()
    wallets = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # 4. تهيئة الترقيم
    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap5')
    
    # 5. التحديث الذكي: إذا كان الطلب قادماً عبر AJAX، نعيد فقط الجزء المحدث
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/partials/wallet_table_body.html', 
                               wallets=wallets, 
                               pagination=pagination)
    
    # إذا كان الطلب عادياً، نعيد الصفحة كاملة
    return render_template('admin/wallet_app.html', 
                           wallets=wallets, 
                           pagination=pagination)

# باقي المسارات
@wallet_app.route('/wallet/search_suppliers')
def search_suppliers():
    term = request.args.get('term', '')
    suppliers = Supplier.query.filter(
        or_(Supplier.search_name.contains(term), Supplier.search_phone.contains(term))
    ).limit(10).all()
    results = [{'id': s.id, 'text': f"{s.trade_name} - {s.owner_phone}"} for s in suppliers]
    return jsonify({'results': results})

@wallet_app.route('/wallet/manage/<int:supplier_id>')
def manage_wallet(supplier_id):
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    return render_template('admin/view_wallet.html', wallet=wallet)
