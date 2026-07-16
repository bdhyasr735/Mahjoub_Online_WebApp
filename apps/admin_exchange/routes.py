# coding: utf-8
# 📂 apps/admin_exchange/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models.exchange_db import ExchangeRate

# تم تعديل الاسم ليتوافق مع المعايير (admin_exchange_bp)
admin_exchange_bp = Blueprint(
    'admin_exchange_bp', 
    __name__, 
    template_folder='templates'
)

@admin_exchange_bp.route('/exchange-rates', methods=['GET', 'POST'])
@login_required
def manage_rates():
    # التحقق من الصلاحيات
    user_role = getattr(current_user, 'role', None)
    if not (getattr(current_user, 'is_admin', False) or user_role == 'Owner'):
        flash("غير مصرح لك بالوصول لهذه الصفحة.", "danger")
        return redirect(url_for('admin_dashboard_bp.dashboard'))

    # معالجة إضافة أو تحديث سعر الصرف
    if request.method == 'POST':
        code = request.form.get('currency_code', '').upper().strip()
        raw_rate = request.form.get('rate')
        
        if not code or not raw_rate:
            flash("يرجى إدخال رمز العملة والسعر بشكل صحيح.", "warning")
            return redirect(url_for('admin_exchange_bp.manage_rates'))
        
        try:
            new_rate = float(raw_rate)
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
        except ValueError:
            flash("سعر الصرف يجب أن يكون رقماً صحيحاً أو عشرياً.", "danger")
        
        return redirect(url_for('admin_exchange_bp.manage_rates'))

    # جلب كافة الأسعار للعرض
    rates = ExchangeRate.query.all()
    return render_template('admin/exchange_rates.html', rates=rates)
