# 📂 apps/admin_exchange/routes.py
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models.exchange_db import ExchangeRate

# تحديد المسار للقوالب
admin_exchange_bp = Blueprint(
    'admin_exchange', 
    __name__, 
    template_folder='templates'
)

@admin_exchange_bp.route('/exchange-rates', methods=['GET', 'POST'])
@login_required
def manage_rates():
    # التحقق من الصلاحيات (Admin أو Owner فقط)
    user_role = getattr(current_user, 'role', None)
    
    if user_role not in ['admin', 'Owner']:
        flash("غير مصرح لك بالوصول لهذه الصفحة.", "danger")
        return redirect(url_for('admin_dashboard.dashboard'))

    # معالجة إضافة أو تحديث سعر الصرف
    if request.method == 'POST':
        code = request.form.get('currency_code', '').upper() # تحويل الرمز لحروف كبيرة لتوحيد القاعدة
        new_rate = request.form.get('rate')
        
        if not code or not new_rate:
            flash("يرجى إدخال رمز العملة والسعر بشكل صحيح.", "warning")
            return redirect(url_for('admin_exchange.manage_rates'))
        
        # التحديث أو الإضافة
        rate_entry = ExchangeRate.query.filter_by(currency_code=code).first()
        
        if rate_entry:
            rate_entry.rate_to_sar = new_rate
            rate_entry.last_updated_by = current_user.username
        else:
            new_entry = ExchangeRate(
                currency_code=code, 
                rate_to_sar=new_rate, 
                last_updated_by=current_user.username
            )
            db.session.add(new_entry)
        
        db.session.commit()
        flash(f"تم اعتماد سعر {code} بنجاح.", "success")
        return redirect(url_for('admin_exchange.manage_rates'))

    # جلب كافة الأسعار للعرض في الجدول
    rates = ExchangeRate.query.all()
    
    # عرض الصفحة مع تمرير البيانات (المسار الآن admin/exchange_rates.html صحيح تماماً)
    return render_template('admin/exchange_rates.html', rates=rates)
