# coding: utf-8
# 📂 apps/suppliers_dashboard/settings_routes.py

from flask import Blueprint, render_template, abort, session, request, flash, redirect, url_for
from flask_login import login_required, current_user
import traceback

from apps.models import db, Supplier, SupplierWallet
from apps.models.supplier_profile_db import SupplierProfile
from apps.data.yemen_data import YEMEN_GOVERNORATES

settings_bp = Blueprint(
    'suppliers_settings',
    __name__,
    template_folder='templates'
)


def get_supplier_context():
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return None
        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id
        supplier = db.session.get(Supplier, supplier_id)
        if supplier:
            wallet = db.session.execute(
                db.select(SupplierWallet).filter_by(supplier_id=supplier.id)
            ).unique().scalar_one_or_none()
            supplier.wallet = wallet
        return supplier
    except Exception as e:
        print(f"❌ خطأ في get_supplier_context: {e}")
        return None


@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    try:
        supplier = get_supplier_context()
        if not supplier:
            flash('❌ لم يتم العثور على المورد', 'danger')
            return redirect('/supplier/login')
        
        # ✅ معالجة POST
        if request.method == 'POST':
            try:
                # ✅ تحديث بيانات المورد الأساسية
                supplier.trade_name = request.form.get('trade_name', supplier.trade_name)
                # ❌ owner_name لا يتم تحديثه (للقراءة فقط)
                # supplier.owner_name = request.form.get('owner_name', supplier.owner_name)
                
                # ✅ تحديث رقم الهاتف
                new_phone = request.form.get('phone', '')
                if new_phone and new_phone != supplier.phone:
                    supplier.phone = new_phone
                
                # ✅ تحديث الملف الشخصي
                profile = getattr(supplier, 'supplier_profile', None)
                if not profile:
                    profile = SupplierProfile(supplier_id=supplier.id)
                    db.session.add(profile)
                
                # ✅ حفظ البيانات الجديدة
                profile.email = request.form.get('email', '')
                profile.address = request.form.get('address', '')
                profile.description = request.form.get('description', '')
                profile.governorate = request.form.get('governorate', '')
                profile.city = request.form.get('city', '')
                
                db.session.commit()
                flash('✅ تم تحديث البيانات بنجاح', 'success')
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ خطأ في حفظ البيانات: {e}")
                flash(f'❌ حدث خطأ: {str(e)}', 'danger')
            
            return redirect(url_for('suppliers_settings.settings'))
        
        # ✅ عرض الصفحة مع تمرير المحافظات
        return render_template(
            'suppliers/settings.html',
            supplier=supplier,
            governorates=YEMEN_GOVERNORATES
        )
        
    except Exception as e:
        # ✅ عرض تفاصيل الخطأ كاملة
        error_details = traceback.format_exc()
        print(f"❌ خطأ في settings: {error_details}")
        
        return f"""
        <div style="direction: rtl; font-family: Tahoma; padding: 30px; text-align: center;">
            <h2 style="color: #d9534f;">❌ خطأ في صفحة الإعدادات</h2>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: right; margin: 20px auto; max-width: 800px; overflow: auto; border: 1px solid #ddd;">
                <p><strong>تفاصيل الخطأ:</strong></p>
                <pre style="background: #fff; padding: 15px; border-radius: 5px; border: 1px solid #ddd; font-size: 12px; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word;">{error_details}</pre>
            </div>
            <a href="/supplier/settings" style="background: #2d0b36; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 5px;">محاولة مرة أخرى</a>
        </div>
        """, 500
