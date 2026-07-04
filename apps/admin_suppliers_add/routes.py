# 📂 apps/admin_suppliers_add/routes.py

import secrets
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_required
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet

# إعداد الـ Blueprint
admin_suppliers_add_bp = Blueprint('admin_suppliers_add_bp', __name__, template_folder='templates')

@admin_suppliers_add_bp.route('/check-availability', methods=['POST'])
@login_required
def check_availability():
    """دالة للتحقق اللحظي من توفر البيانات"""
    data = request.get_json()
    field = data.get('field')
    value = data.get('value')
    
    if not value:
        return jsonify({'available': False})

    # التحقق اللحظي لكل الحقول بما فيها اسم المالك
    if field == 'username':
        exists = Supplier.query.filter_by(username=value).first()
    elif field == 'phone':
        # البحث باستخدام آخر 9 أرقام كما هو مخزن في الموديل
        exists = Supplier.query.filter_by(search_phone=str(value)[-9:]).first()
    elif field == 'trade_name':
        exists = Supplier.query.filter_by(trade_name=value).first()
    elif field == 'owner_name':
        exists = Supplier.query.filter_by(owner_name=value).first()
    else:
        return jsonify({'available': False})
        
    return jsonify({'available': not exists})

@admin_suppliers_add_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier_or_staff():
    if request.method == 'POST':
        try:
            # استقبال البيانات
            owner_name = request.form.get('owner_name', '').strip()
            username = request.form.get('username', '').strip()
            trade_name = request.form.get('trade_name', '').strip()
            phone = request.form.get('phone', '').strip()
            
            # التحقق النهائي (تجنب التكرار في حال تجاوز المستخدم للتحقق اللحظي)
            if Supplier.query.filter((Supplier.username == username) | (Supplier.search_phone == phone[-9:])).first():
                flash("اسم المستخدم أو رقم الهاتف مستخدم مسبقاً", "danger")
                return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

            # توليد كلمة مرور عشوائية قوية
            temp_password = secrets.token_hex(4)

            # إنشاء المورد
            new_supplier = Supplier(
                owner_name=owner_name,
                username=username,
                trade_name=trade_name,
                phone=phone,
                status='active',
                created_at=datetime.utcnow()
            )
            new_supplier.set_password(temp_password)
            
            db.session.add(new_supplier)
            db.session.commit()

            # جلب المحفظة التي تم إنشاؤها تلقائياً
            wallet = SupplierWallet.query.filter_by(supplier_id=new_supplier.id).first()
            wallet_code = wallet.wallet_code if wallet else "N/A"
            
            # تخزين البيانات في الجلسة لعرضها في النافذة المنبثقة
            session['new_user_data'] = {
                'trade_name': trade_name,
                'username': username,
                'password': temp_password,
                'wallet_code': wallet_code
            }
            
            return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving supplier: {str(e)}")
            flash("حدث خطأ تقني، يرجى المحاولة لاحقاً", "danger")
            return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

    # معالجة عرض الصفحة: استخدام pop لحذف البيانات من الجلسة بعد العرض مباشرة
    new_user = session.pop('new_user_data', None)
    return render_template('admin_suppliers_add/admin_suppliers_add.html', new_user=new_user)
