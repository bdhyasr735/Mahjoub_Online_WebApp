# coding: utf-8
# 📂 apps/suppliers_dashboard/settings_routes.py

from flask import Blueprint, render_template, abort, session, request, flash, redirect, url_for
from flask_login import login_required, current_user
import traceback

from apps.models import db, Supplier, SupplierWallet
from apps.models.supplier_profile_db import SupplierProfile
from apps.data.yemen_governorates import YEMEN_GOVERNORATES
from apps.data.store_categories import STORE_CATEGORIES
from apps.data.yemen_banks import YEMEN_BANKS
from apps.data.financial_companies import FINANCIAL_COMPANIES

settings_bp = Blueprint(
    'suppliers_settings',
    __name__,
    template_folder='templates'
)


def get_supplier_context():
    """
    جلب بيانات المورد والمحفظة من قاعدة البيانات
    مع التحقق من صلاحية المستخدم
    """
    try:
        # ✅ التحقق من نوع المستخدم
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return None
        
        # ✅ تحديد supplier_id
        if user_type == 'staff':
            supplier_id = getattr(current_user, 'supplier_id', None)
        else:
            supplier_id = current_user.id
        
        if not supplier_id:
            return None
        
        # ✅ جلب المورد
        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            return None
        
        # ✅ جلب المحفظة
        wallet = db.session.execute(
            db.select(SupplierWallet).filter_by(supplier_id=supplier.id)
        ).unique().scalar_one_or_none()
        supplier.wallet = wallet
        
        return supplier
        
    except Exception as e:
        print(f"❌ خطأ في get_supplier_context: {e}")
        return None


@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required  # ✅ يمنع الوصول غير المسجل
def settings():
    """
    صفحة إعدادات المتجر - فقط للموردين المسجلين
    """
    try:
        # ✅ التحقق من وجود المورد
        supplier = get_supplier_context()
        if not supplier:
            flash('❌ يرجى تسجيل الدخول أولاً', 'danger')
            return redirect(url_for('suppliers_auth.login'))  # ✅ إعادة التوجيه لبوابة الدخول
        
        # ✅ معالجة POST (حفظ البيانات)
        if request.method == 'POST':
            try:
                # ✅ تحديث اسم المتجر
                supplier.trade_name = request.form.get('trade_name', supplier.trade_name)
                
                # ❌ owner_name لا يتم تحديثه (للقراءة فقط - أمان)
                # supplier.owner_name = request.form.get('owner_name', supplier.owner_name)
                
                # ✅ تحديث رقم الهاتف مع التحقق
                new_phone = request.form.get('phone', '').strip()
                if new_phone and len(new_phone) == 9 and new_phone.isdigit():
                    if new_phone != supplier.phone:
                        supplier.phone = new_phone
                elif new_phone:
                    flash('⚠️ رقم الهاتف يجب أن يكون 9 أرقام', 'warning')
                    return redirect(url_for('suppliers_settings.settings'))
                
                # ✅ تحديث الملف الشخصي
                profile = getattr(supplier, 'supplier_profile', None)
                if not profile:
                    profile = SupplierProfile(supplier_id=supplier.id)
                    db.session.add(profile)
                
                # ✅ حفظ جميع البيانات
                profile.email = request.form.get('email', '').strip()
                profile.address = request.form.get('address', '').strip()
                profile.description = request.form.get('description', '').strip()
                profile.governorate = request.form.get('governorate', '').strip()
                profile.city = request.form.get('city', '').strip()
                profile.category = request.form.get('category', '').strip()
                profile.bank_name = request.form.get('bank_name', '').strip()
                profile.bank_account = request.form.get('bank_account', '').strip()
                profile.company_name = request.form.get('financial_company', '').strip()
                profile.id_number = request.form.get('id_number', '').strip()
                profile.commercial_reg = request.form.get('commercial_reg', '').strip()
                
                db.session.commit()
                flash('✅ تم تحديث بيانات المتجر بنجاح', 'success')
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ خطأ في حفظ البيانات: {e}")
                flash(f'❌ حدث خطأ أثناء الحفظ: {str(e)}', 'danger')
            
            return redirect(url_for('suppliers_settings.settings'))
        
        # ✅ عرض الصفحة مع تمرير جميع البيانات
        return render_template(
            'suppliers/settings.html',
            supplier=supplier,
            governorates=YEMEN_GOVERNORATES,
            categories=STORE_CATEGORIES,
            banks=YEMEN_BANKS,
            financial_companies=FINANCIAL_COMPANIES
        )
        
    except Exception as e:
        # ✅ عرض تفاصيل الخطأ للمطور
        error_details = traceback.format_exc()
        print(f"❌ خطأ في settings: {error_details}")
        
        # ✅ للمستخدم العادي: رسالة مبسطة
        flash('❌ حدث خطأ تقني، يرجى المحاولة لاحقاً', 'danger')
        return redirect(url_for('suppliers_dashboard.dashboard'))
