# coding: utf-8
# 📂 apps/admin_suppliers_add/routes.py

import secrets
import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_required
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet

admin_suppliers_add_bp = Blueprint('admin_suppliers_add_bp', __name__, template_folder='templates')

@admin_suppliers_add_bp.route('/check_availability', methods=['POST'])
@login_required
def check_availability():
    data = request.get_json()
    field = data.get('field')
    value = data.get('value')
    if not value: return jsonify({'available': False})
    
    exists = False
    if field == 'username': exists = Supplier.query.filter_by(username=value).first()
    elif field == 'phone': exists = Supplier.query.filter_by(search_phone=str(value)[-9:]).first()
    elif field == 'trade_name': exists = Supplier.query.filter_by(trade_name=value).first()
    return jsonify({'available': not exists})

@admin_suppliers_add_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier_or_staff():
    if request.method == 'POST':
        try:
            owner_name = request.form.get('owner_name', '').strip()
            username = request.form.get('username', '').strip()
            trade_name = request.form.get('trade_name', '').strip()
            phone = request.form.get('phone', '').strip()
            phone_9 = phone[-9:]
            
            existing = Supplier.query.filter((Supplier.username == username) | (Supplier.search_phone == phone_9)).first()
            if existing:
                flash("اسم المستخدم أو رقم الهاتف مستخدم مسبقاً", "danger")
                return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

            temp_password = secrets.token_hex(4)

            # 1. إنشاء المورد
            new_supplier = Supplier(
                owner_name=owner_name,
                username=username,
                trade_name=trade_name,
                phone=phone,
                search_phone=phone_9,
                status='active'
            )
            new_supplier.set_password(temp_password)
            db.session.add(new_supplier)
            db.session.flush() 

            # 2. إنشاء المحفظة
            new_wallet = SupplierWallet(
                wallet_code=f"MAH-WEL963{new_supplier.id}", 
                supplier_id=new_supplier.id
            )
            db.session.add(new_wallet)
            db.session.commit()
            
            session['new_user_data'] = {
                'trade_name': trade_name,
                'username': username,
                'password': temp_password,
                'wallet_code': new_wallet.wallet_code
            }
            
            return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving supplier: {str(e)}")
            flash("حدث خطأ تقني، يرجى المحاولة لاحقاً", "danger")
            return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

    new_user = session.pop('new_user_data', None)
    return render_template('admin_suppliers_add/admin_suppliers_add.html', new_user=new_user)
