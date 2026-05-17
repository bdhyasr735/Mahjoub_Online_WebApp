# coding: utf-8
# 🏢 محرك تعميد الموردين السيادي - منصة محجوب أونلاين 2026

from flask import render_template, request, redirect, url_for, flash
from apps import db
from apps.models.admin_db import AdminUser  # أو موديل المورد الخاص بك
from apps.models.wallet_db import Wallet    # استيراد موديل المحفظة الثلاثية
# ... أي استيرادات أخرى تحتاجها هنا ...

@admin_suppliers.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        # 1. استقبال بيانات المورد الجديد من الواجهة
        sovereign_id = request.form.get('sovereign_id')
        username = request.form.get('username')
        # ... بقية الحقول (الهاتف، كلمة المرور، إلخ) ...

        try:
            # 2. إنشاء كائن المورد الجديد وحفظه
            new_supplier = AdminUser(
                sovereign_id=sovereign_id,
                username=username,
                # ... بقية الحقول ...
            )
            db.session.add(new_supplier)
            db.session.flush() # عمل Flush للحصول على الـ ID الخاص بالمورد قبل الـ Commit

            # 3. 💳 الحقن المالي التلقائي: إنشاء المحفظة الثلاثية بالـ ID المولد فوراً
            supplier_wallet = Wallet(
                supplier_id=new_supplier.id, # ربط المحفظة بالمورد الجديد
                # عملة الريال اليمني
                yer_total=0.0,
                yer_available=0.0,
                yer_pending=0.0,
                yer_withdrawn=0.0,
                # عملة الريال السعودي
                sar_total=0.0,
                sar_available=0.0,
                sar_pending=0.0,
                sar_withdrawn=0.0,
                # عملة الدولار الأمريكي
                usd_total=0.0,
                usd_available=0.0,
                usd_pending=0.0,
                usd_withdrawn=0.0
            )
            db.session.add(supplier_wallet)
            
            # 4. حفظ الكتلة البرمجية كاملة في قاعدة بيانات Railway
            db.session.commit()
            flash('تم تعميد المورد بنجاح وتوليد محفظته المالية الثلاثية تلقائياً!', 'success')
            return redirect(url_for('admin_dashboard.list_suppliers'))

        except Exception as e:
            db.session.rollback()
            flash(f'⚠️ فشل الإجراء السيادي: {str(e)}', 'danger')
            
    return render_template('admin/add_supplier.html', owner=current_user)
