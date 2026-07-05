# 📂 apps/admin_exchange/routes.py
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models.exchange_db import ExchangeRate

# تحديد المسار الصحيح للقوالب داخل موديول admin_exchange
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
admin_exchange_bp = Blueprint('admin_exchange', __name__, template_folder=template_dir)

@admin_exchange_bp.route('/exchange-rates', methods=['GET', 'POST'])
@login_required
def manage_rates():
    # التحقق من الصلاحيات باستخدام حقل 'role' المعتمد في AdminStaff
    # التحقق يشمل 'admin' للموظفين و 'Owner' للمالك (أنت)
    user_role = getattr(current_user, 'role', None)
    
    if user_role not in ['admin', 'Owner']:
        # طباعة للتحقق في سجلات النظام في حال الرفض
        print(f"DEBUG: Access denied. User role is: {user_role}")
        flash(f"غير مصرح لك بالوصول (رتبتك الحالية: {user_role})", "danger")
        return redirect(url_for('admin_dashboard.dashboard'))

    if request.method == 'POST':
        code = request.form.get('currency_code')
        new_rate = request.form.get('rate')
        
        # التحديث أو الإضافة
        # النظام سيتعامل مع last_updated_by تلقائياً ويقوم بتشفيره
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
        flash(f"تم تحديث سعر الصرف لعملة {code} بنجاح", "success")
        return redirect(url_for('admin_exchange.manage_rates'))

    # جلب كافة الأسعار للعرض في الجدول
    # القالب سيقوم بفك التشفير تلقائياً عند عرض last_updated_by
    rates = ExchangeRate.query.all()
    return render_template('admin/exchange_rates.html', rates=rates)
