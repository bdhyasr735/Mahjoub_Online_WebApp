# coding: utf-8
# 📂 apps/admin_suppliers_add/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from apps.extensions import db
from apps.models.suppliers_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from sqlalchemy.exc import IntegrityError
import secrets

admin_suppliers_add_bp = Blueprint(
    'admin_suppliers_add_bp', 
    __name__, 
    template_folder='templates'
)

@admin_suppliers_add_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier_or_staff():
    """نقطة دخول موحدة لإضافة مورد (مالك) أو موظف مع أتمتة المحفظة والتعميد."""
    
    if request.method == 'POST':
        action_type = request.form.get('action_type') # 'owner' or 'staff'
        temp_password = secrets.token_hex(4) # توليد كلمة مرور مؤقتة احترافية
        
        try:
            if action_type == 'owner':
                # 1. إنشاء المورد (المالك)
                new_supplier = Supplier(
                    username=request.form.get('username'),
                    trade_name=request.form.get('trade_name'),
                    rank=request.form.get('rank', 'bronze'), # التعامل مع الرتبة
                    status='active'
                )
                new_supplier.phone = request.form.get('phone') 
                new_supplier.set_password(temp_password)
                
                db.session.add(new_supplier)
                db.session.commit() # الـ Auto-Discovery ينشئ المحفظة هنا
                
                db.session.refresh(new_supplier) # لجلب بيانات المحفظة بعد الإنشاء
                wallet_code = new_supplier.wallet.wallet_code if new_supplier.wallet else "قيد الإنشاء"
                
                flash(f"✅ تم تسجيل المورد بنجاح! | المورد: {new_supplier.trade_name} | المحفظة: {wallet_code} | كلمة المرور المؤقتة: {temp_password} | محجوب اونلاين | سوقك الذكي", "success")
                
            elif action_type == 'staff':
                # 2. إضافة الموظف وربطه بالمورد
                new_staff = SupplierStaff(
                    supplier_id=request.form.get('supplier_id'),
                    username=request.form.get('username'),
                    email=request.form.get('email'),
                    role=request.form.get('role', 'worker')
                )
                new_staff.set_password(temp_password)
                
                db.session.add(new_staff)
                db.session.commit()
                flash(f"✅ تم إضافة الموظف بنجاح! | اسم المستخدم: {new_staff.username} | كلمة المرور المؤقتة: {temp_password} | محجوب اونلاين | سوقك الذكي", "success")
            
            return redirect(url_for('admin_suppliers_add_bp.add_supplier_or_staff'))

        except IntegrityError:
            db.session.rollback()
            flash("❌ خطأ: اسم المستخدم أو البريد الإلكتروني مسجل مسبقاً في النظام.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"⚠️ حدث خطأ تقني: {str(e)}", "danger")

    suppliers = Supplier.query.all()
    return render_template('admin_suppliers_add/admin_suppliers_add.html', suppliers=suppliers)
