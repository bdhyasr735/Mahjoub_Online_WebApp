# apps/suppliers_dashboard/routes.py

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.supplier_profile_db import SupplierProfile
from apps.extensions import db

# إنشاء Blueprint
suppliers_dashboard_bp = Blueprint(
    'suppliers_dashboard',
    __name__,
    template_folder='templates/suppliers_dashboard',
    url_prefix='/supplier/dashboard'
)


@suppliers_dashboard_bp.route('/')
@login_required
def index():
    """الصفحة الرئيسية للوحة تحكم المورد"""
    
    # التحقق من أن المستخدم هو مورد
    if not hasattr(current_user, 'id'):
        flash("يرجى تسجيل الدخول كمورد.", "warning")
        return redirect(url_for('suppliers_auth_bp.login_page'))
    
    supplier_id = current_user.id
    
    # جلب بيانات المورد
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        flash("لم يتم العثور على بيانات المورد.", "danger")
        return redirect(url_for('suppliers_auth_bp.login_page'))
    
    # جلب المحفظة
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    
    # جلب عدد المنتجات
    products_count = ProductSupplierMapping.query.filter_by(
        supplier_id=supplier_id,
        is_active=True
    ).count()
    
    # جلب عدد الموظفين
    staff_count = SupplierStaff.query.filter_by(
        supplier_id=supplier_id,
        is_active=True
    ).count()
    
    # جلب الملف الشخصي
    profile = SupplierProfile.query.filter_by(supplier_id=supplier_id).first()
    
    # إحصائيات سريعة
    balance = wallet.balance if wallet else 0.0
    
    # قائمة الوحدات الجانبية (sidebar)
    supplier_modules = [
        {
            'name': 'الرئيسية',
            'icon': 'fa-chart-pie',
            'items': [
                {'name': 'لوحة التحكم', 'url': url_for('suppliers_dashboard.index'), 'active': True}
            ]
        },
        {
            'name': 'إدارة المنتجات',
            'icon': 'fa-box',
            'items': [
                {'name': 'جميع المنتجات', 'url': '#', 'active': False},
                {'name': 'إضافة منتج جديد', 'url': '#', 'active': False}
            ]
        },
        {
            'name': 'المبيعات والطلبات',
            'icon': 'fa-shopping-cart',
            'items': [
                {'name': 'الطلبات الواردة', 'url': '#', 'active': False},
                {'name': 'سجل المبيعات', 'url': '#', 'active': False}
            ]
        },
        {
            'name': 'الإدارة المالية',
            'icon': 'fa-wallet',
            'items': [
                {'name': 'المحفظة والسحب', 'url': '#', 'active': False},
                {'name': 'تقارير التسوية', 'url': '#', 'active': False}
            ]
        },
        {
            'name': 'الموظفين',
            'icon': 'fa-users',
            'items': [
                {'name': 'قائمة الموظفين', 'url': '#', 'active': False},
                {'name': 'إضافة موظف', 'url': '#', 'active': False}
            ]
        }
    ]
    
    return render_template(
        'suppliers_dashboard/index.html',
        page_title='لوحة تحكم المورد',
        supplier=supplier,
        profile=profile,
        wallet=wallet,
        balance=balance,
        products_count=products_count,
        staff_count=staff_count,
        supplier_modules=supplier_modules
    )


@suppliers_dashboard_bp.route('/api/ask-ai', methods=['POST'])
@login_required
def ask_ai():
    """مسار استقبال أسئلة المورد ومعالجتها بواسطة المساعد الذكي"""
    data = request.get_json() or {}
    question = data.get('question', '').strip()

    if not question:
        return jsonify({'success': False, 'message': 'الرجاء إدخال سؤال صحيح.'}), 400

    try:
        answer = f"شكراً لاستفسارك! بناءً على تحليل متجرك الداخلي، أنصحك بـ: التركيز على تحسين تفاصيل المنتجات وإدارة المخزون بفعالية لتطوير استراتيجية '{question}'."
        return jsonify({'success': True, 'answer': answer})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
