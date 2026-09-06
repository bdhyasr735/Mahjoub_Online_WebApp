# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from apps.extensions import db

# تعريف اسم الموديول وخصائصه الأساسية للوحة التحكم
MODULE_NAME = "محفظة المورد"
DISPLAY_NAME = "محفظة المورد"
MODULE_ICON = "fa-wallet"
SHOW_IN_SUPPLIER = True  # ليظهر ضمن لوحة تحكم الموردين

# تعريف مسار البلوبرينت الخاص بالمحفظة
supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/supplier/wallet'
)

@supplier_wallet_bp.route('/')
@login_required
def wallet_overview():
    """عرض صفحة المحفظة الرئيسية للمورد وسجل المعاملات والأرصدة"""
    # التحقق من أن المستخدم الحالي هو مورد أو موظف تابع له
    supplier_id = getattr(current_user, 'supplier_id', None)
    if not supplier_id and hasattr(current_user, 'id'):
        # إذا كان الحساب نفسه هو المورد الأساسي
        if getattr(current_user, 'role', None) == 'supplier' or session_is_supplier():
            supplier_id = current_user.id

    if not supplier_id:
        abort(403)

    try:
        from apps.models.wallet_db import SupplierWallet, WalletTransaction
        wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
        
        if not wallet:
            # إنشاء محفظة تلقائياً إذا لم تكن موجودة للمورد
            wallet = SupplierWallet(supplier_id=supplier_id, balance=0.0, locked_balance=0.0)
            db.session.add(wallet)
            db.session.commit()

        transactions = WalletTransaction.query.filter_by(wallet_id=wallet.id).order_by(WalletTransaction.created_at.desc()).all()

        return render_template(
            'supplier_wallet/overview.html',
            wallet=wallet,
            transactions=transactions
        )
    except Exception as e:
        db.session.rollback()
        flash(f"حدث خطأ أثناء استبيان بيانات المحفظة: {str(e)}", "danger")
        return redirect(url_for('supplier_wallet.wallet_overview'))

def session_is_supplier():
    """دالة مساعدة للتحقق من نوع الجلسة الحالية"""
    from flask import session
    return session.get('user_type') in ['supplier', 'supplier_staff']

def register_module(app):
    """دالة التسجيل القياسية المطلوبة من النظام الديناميكي لتحميل الموديول"""
    # تسجيل البلوبرينت في التطبيق الرئيسي
    if supplier_wallet_bp.name not in app.blueprints:
        app.register_blueprint(supplier_wallet_bp)
    
    # ربط الخيارات والعناصر الخاصة بالقائمة الجانبية للوحة الموردين
    if not hasattr(app, 'supplier_modules'):
        app.supplier_modules = {}
        
    app.supplier_modules['supplier_wallet'] = {
        "display_name": DISPLAY_NAME,
        "icon": MODULE_ICON,
        "links": {
            "supplier_wallet.wallet_overview": "إدارة المحفظة والأرصدة"
        }
    }
    
    print("🟢 [موديول محفظة الموردين]: تم تسجيله وتنشيطه بنجاح عبر ملف التسجيل (registry.py).")

# القوائم والروابط البديلة لضمان التوافق التام مع فاحص النظام
NAV_ITEMS = [
    {
        "endpoint": "supplier_wallet.wallet_overview",
        "title": "محفظة الأرباح والمدفوعات"
    }
]

LINKS = {
    "supplier_wallet.wallet_overview": "محفظة الأرباح والمدفوعات"
}

def get_menu_items():
    return LINKS
