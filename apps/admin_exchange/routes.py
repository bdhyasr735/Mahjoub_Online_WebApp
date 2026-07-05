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
    
    # تحسين التحقق من الصلاحيات ليشمل معرفة نوع المستخدم (AdminUser)
    if not (getattr(current_user, 'is_admin', False) or user_role == 'Owner'):
        flash("غير مصرح لك بالوصول لهذه الصفحة.", "danger")
        return redirect(url_for('admin_dashboard.dashboard'))

    # معالجة إضافة أو تحديث سعر الصرف
    if request.method == 'POST':
        code = request.form.get('currency_code', '').upper().strip()
        raw_rate = request.form.get('rate')
        
        if not code or not raw_rate:
            flash("يرجى إدخال رمز العملة والسعر بشكل صحيح.", "warning")
            return redirect(url_for('admin_exchange.manage_rates'))
        
        try:
            # تحويل السعر إلى رقم عشري لضمان الحفظ في قاعدة البيانات
            new_rate = float(raw_rate)
            
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
        except ValueError:
            flash("سعر الصرف يجب أن يكون رقماً صحيحاً أو عشرياً.", "danger")
        
        return redirect(url_for('admin_exchange.manage_rates'))

    # جلب كافة الأسعار للعرض في الجدول
    rates = ExchangeRate.query.all()
    
    # عرض الصفحة
    return render_template('admin/exchange_rates.html', rates=rates)
