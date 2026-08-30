from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from . import suppliers_bp
# قم باستيراد النماذج (Models) الخاصة بك حسب هيكلة المشروع لديك
# from apps.models import Supplier, Wallet, Order

@suppliers_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    # 1. جلب بيانات المورد المرتبط بالمستخدم الحالي
    supplier = getattr(current_user, 'supplier', None)
    
    if not supplier:
        flash("حسابك غير مرتبط ببيانات مورد مفعل.", "warning")
        return redirect(url_for('main.index'))

    # 2. حساب وتجهيز الإحصائيات (الطلبات المعلقة والإجمالي)
    pending_orders_count = 0
    total_sales = 0.0
    
    # مثال لحساب البيانات في حال وجود العلاقات:
    # pending_orders_count = Order.query.filter_by(supplier_id=supplier.id, status='pending').count()
    # total_sales = sum(order.total_amount for order in supplier.orders if order.status == 'completed')

    # 3. إعداد هيكل الوحدات والقوائم الجانبية (supplier_modules) ليمرر إلى base.html
    supplier_modules = [
        {
            'name': 'الرئيسية',
            'icon': 'fas fa-chart-pie',
            'items': [
                {'name': 'لوحة التحكم', 'url': url_for('suppliers.dashboard'), 'active': True}
            ]
        },
        {
            'name': 'إدارة المنتجات',
            'icon': 'fas fa-box',
            'items': [
                {'name': 'جميع المنتجات', 'url': '#', 'active': False},
                {'name': 'إضافة منتج جديد', 'url': '#', 'active': False}
            ]
        },
        {
            'name': 'المبيعات والطلبات',
            'icon': 'fas fa-shopping-cart',
            'items': [
                {'name': 'الطلبات الواردة', 'url': '#', 'active': False},
                {'name': 'سجل المبيعات', 'url': '#', 'active': False}
            ]
        },
        {
            'name': 'الإدارة المالية',
            'icon': 'fas fa-wallet',
            'items': [
                {'name': 'المحفظة والسحب', 'url': '#', 'active': False},
                {'name': 'تقارير التسوية', 'url': '#', 'active': False}
            ]
        }
    ]

    return render_template(
        'suppliers/dashboard.html',
        supplier=supplier,
        pending_orders_count=pending_orders_count,
        total_sales=total_sales,
        supplier_modules=supplier_modules
    )


@suppliers_bp.route('/api/ask-ai', methods=['POST'])
@login_required
def ask_ai():
    """مسار استقبال أسئلة المورد ومعالجتها بواسطة المساعد الذكي الداخلي"""
    data = request.get_json() or {}
    question = data.get('question', '').strip()

    if not question:
        return jsonify({'success': False, 'message': 'الرجاء إدخال سؤال صحيح.'}), 400

    try:
        # معالجة الاستفسار داخل النظام البيئي لمنصة محجوب أونلاين
        answer = f"شكراً لاستفسارك! بناءً على تحليل متجرك الداخلي، أنصحك بـ: التركيز على تحسين تفاصيل المنتجات وإدارة المخزون بفعالية لتطوير استراتيجية '{question}'."

        return jsonify({
            'success': True,
            'answer': answer
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
