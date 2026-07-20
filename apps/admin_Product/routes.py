from flask import Blueprint, render_template, request, redirect, url_for, flash

# تعريف الـ Blueprint باسم admin_product_bp ليتوافق مع url_for في القالب
admin_product_bp = Blueprint('admin_product_bp', __name__, template_folder='templates')


@admin_product_bp.route('/products', methods=['GET'])
def manage_products():
    """
    عرض قائمة المنتجات مع دعم البحث برمز/اسم المنتج والتصفح الصفحي (Pagination).
    يدعم أيضاً طلبات الـ AJAX القادمة من السكريبت المدمج في القالب.
    """
    search_query = request.args.get('title', '', type=str).strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10  # عدد المنتجات في كل صفحة

    # -------------------------------------------------------------
    # جلب البيانات من قاعدة البيانات أو الخدمة الخارجية (مثل Qomra / DB)
    # -------------------------------------------------------------
    pagination = {
        'currentPage': page,
        'totalPages': 1,  # يُحسب بناءً على Math.ceil(total_count / per_page)
        'totalItems': 0
    }
    
    products = []  # مصفوفة المنتجات المسترجعة

    return render_template(
        'admin/admin_Product.html',
        products=products,
        pagination=pagination,
        search=search_query
    )


@admin_product_bp.route('/products/add', methods=['GET', 'POST'])
def add_product():
    """
    مسار إضافة منتج جديد (تنتقل إليه المسؤولية عند النقر على زر 'إضافة منتج').
    """
    if request.method == 'POST':
        # معالجة حفظ المنتج الجديد
        flash('تمت إضافة المنتج بنجاح', 'success')
        return redirect(url_for('admin_product_bp.manage_products'))

    return render_template('admin/add_product.html')


# ✅ تم تعديل المتغير إلى <path:qid> ليقبل الشرطات المائلة داخل qid://qumra/...
@admin_product_bp.route('/products/edit/<path:qid>', methods=['GET', 'POST'])
def edit_product(qid):
    """
    مسار تعديل المنتج بناءً على الـ qid الخاص به
    (تنتقل إليه المسؤولية عند النقر على بطاقة المنتج).
    """
    if request.method == 'POST':
        # معالجة تحديث بيانات المنتج
        flash('تم تحديث بيانات المنتج بنجاح', 'success')
        return redirect(url_for('admin_product_bp.manage_products'))

    # جلب تفاصيل المنتج باستخدام qid
    # product = get_product_by_qid(qid)

    return render_template('admin/edit_product.html', qid=qid)
