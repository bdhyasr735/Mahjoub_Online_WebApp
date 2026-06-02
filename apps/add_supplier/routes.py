# coding: utf-8
from flask import Blueprint, render_template, request, redirect, url_for, flash
from apps.extensions import db
from apps.models import Supplier  # استيراد من مجمع النماذج الموحد

# تعريف الـ Blueprint للمصنع
add_supplier = Blueprint('add_supplier', __name__)

@add_supplier.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        try:
            # هنا يتم إنشاء المورد باستخدام البيانات القادمة من النموذج
            # لاحظ أننا نستخدم خصائص التشفير التلقائية (Setter) التي عرفناها في الـ Model
            new_supplier = Supplier(
                sovereign_id=request.form.get('sovereign_id'),
                wallet_code=request.form.get('wallet_code'),
                owner_name=request.form.get('owner_name'),  # سيتم تشفيره تلقائياً
                owner_phone=request.form.get('owner_phone'),
                trade_name=request.form.get('trade_name'),
                shop_phone=request.form.get('shop_phone'),
                bank_acc=request.form.get('bank_acc'),
                identity_number=request.form.get('identity_number'),
                username=request.form.get('username'),
                password=request.form.get('password') # سيتم تشفير كلمة المرور
            )
            
            db.session.add(new_supplier)
            db.session.commit()
            
            flash("✅ تم إضافة المورد بنجاح إلى سجلات المصنع.", "success")
            return redirect(url_for('admin_dashboard.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"❌ حدث خطأ أثناء الإضافة: {str(e)}", "danger")
            
    return render_template('add_supplier.html')
