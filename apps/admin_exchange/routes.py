# 📂 apps/admin_exchange/routes.py
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models.exchange_db import ExchangeRate

# تحديد المسار للقوالب (Flask سيبحث داخل مجلد templates الملحق بالموديول)
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
admin_exchange_bp = Blueprint('admin_exchange', __name__, template_folder='templates')

@admin_exchange_bp.route('/exchange-rates', methods=['GET', 'POST'])
@login_required
def manage_rates():
    # التحقق من الصلاحيات
    user_role = getattr(current_user, 'role', None)
    if user_role not in ['admin', 'Owner']:
        flash("غير مصرح لك بالوصول", "danger")
        return redirect(url_for('admin_dashboard.dashboard'))

    if request.method == 'POST':
        code = request.form.get('currency_code')
        new_rate = request.form.get('rate')
        
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
        flash(f"تم التحديث لعملة {code}", "success")
        return redirect(url_for('admin_exchange.manage_rates'))

    rates = ExchangeRate.query.all()
    
    # التغيير الجوهري هنا: بما أننا داخل Blueprint، 
    # وبما أن مسار الملف هو admin/exchange_rates.html داخل templates
    # يفضل أن يكون استدعاء الملف مطابقاً تماماً للهيكل الموجود في المجلد
    return render_template('admin/exchange_rates.html', rates=rates)
