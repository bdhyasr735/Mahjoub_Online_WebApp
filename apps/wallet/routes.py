# coding: utf-8
# 🏢 محرك تعميد الموردين والربط المالي التلقائي - منصة محجوب أونلاين 2026

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from apps import db
from apps.add_supplier import admin_suppliers  # استيراد البلوبرينت الخاص بحزمة الموردين
from apps.models.admin_db import AdminUser     # استيراد موديل حسابات المسؤولين والموردين
from apps.models.wallet_db import Wallet       # استيراد موديل المحفظة الثلاثية الموحدة
from werkzeug.security import generate_password_hash

@admin_suppliers.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    """
    الواجهة السيادية المخصصة لتعميد الموردين الجدد في قاعدة البيانات
    مع توليد حساب مالي فوري يدعم العملات الثلاث (YER, SAR, USD) تلقائياً.
    """
    if request.method == 'POST':
        sovereign_id = request.form.get('sovereign_id', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # التحقق الأولي من البيانات الأساسية
        if not sovereign_id or not username or not password:
            flash('⚠️ يرجى ملء كافة الحقول الأساسية لإتمام عملية التعميد.', 'warning')
            return render_template('admin/add_supplier.html', owner=current_user)

        try:
            # 1. التحقق من عدم تكرار المعرف السيادي أو اسم المستخدم في قاعدة البيانات
            existing_user = AdminUser.query.filter(
                (AdminUser.sovereign_id == sovereign_id) | (AdminUser.username == username)
            ).first()
            
            if existing_user:
                flash('⚠️ المعرف السيادي أو اسم المستخدم مسجل مسبقاً في النظام!', 'danger')
                return render_template('admin/add_supplier.html', owner=current_user)

            # 2. تشفير كلمة المرور وتعميد كائن المورد الجديد
            hashed_password = generate_password_hash(password, method='scrypt')
            new_supplier = AdminUser(
                sovereign_id=sovereign_id,
                username=username,
                password_hash=hashed_password
                # يمكنك إضافة أي حقول إضافية هنا (مثل الهاتف، اسم المتجر التجاري، إلخ)
            )
            
            db.session.add(new_supplier)
            db.session.flush()  # سحب الـ ID المولد تلقائياً للمورد دون إنهاء الجلسة

            # 3. 💳 الحقن المالي الثلاثي: توليد المحفظة الموحدة للعملات لربطها بالحساب الجديد فوراً
            supplier_wallet = Wallet(
                supplier_id=new_supplier.id,  # ربط المحفظة بالمعرف الفريد للمورد الجديد
                # محفظة الريال اليمني
                yer_total=0.0,
                yer_available=0.0,
                yer_pending=0.0,
                yer_withdrawn=0.0,
                # محفظة الريال السعودي
                sar_total=0.0,
                sar_available=0.0,
                sar_pending=0.0,
                sar_withdrawn=0.0,
                # محفظة الدولار الأمريكي
                usd_total=0.0,
                usd_available=0.0,
                usd_pending=0.0,
                usd_withdrawn=0.0
            )
            
            db.session.add(supplier_wallet)
            
            # 4. حفظ العملية المزدوجة بالكامل لضمان السلامة الهيكلية لقاعدة البيانات (Atomicity)
            db.session.commit()
            flash('🚀 تم تعميد المورد الجديد وتفعيل محفظته المالية للعملات الثلاث بنجاح تام!', 'success')
            return redirect(url_for('admin_dashboard.list_suppliers'))

        except Exception as e:
            db.session.rollback()  # تراجع كامل في حال حدوث أي خلل أثناء العملية لحماية البيانات
            flash(f'❌ فشل الإجراء الحوكمي أثناء الحفظ: {str(e)}', 'danger')
            
    return render_template('admin/add_supplier.html', owner=current_user)
