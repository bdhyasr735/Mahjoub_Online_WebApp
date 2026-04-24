from flask import Blueprint, render_template, request, redirect, url_for, flash
import os

# تحديد مسار المجلد لضمان الوصول لجميع ملفات html داخل templates
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
admin_bp = Blueprint('admin_panel', __name__, template_folder=template_dir)

@admin_bp.route('/', strict_slashes=False)
def dashboard():
    from core.models import Supplier, Product
    try:
        s_count = Supplier.query.count()
        p_count = Product.query.count()
        # التأكد من كتابة الاسم تماماً كما هو في المجلد
        return render_template('dashboard.html', s_count=s_count, p_count=p_count)
    except Exception:
        return render_template('dashboard.html', s_count=0, p_count=0)

@admin_bp.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'علي محجوب' and password == '123456':
            return redirect(url_for('admin_panel.dashboard'))
        else:
            flash('بيانات الولوج غير صحيحة', 'danger')
    return render_template('login.html')

@admin_bp.route('/sync_now', strict_slashes=False)
def sync_now():
    try:
        from core.qumra_sync import qumra_manager
        live_products = qumra_manager.fetch_live_products(limit=15)
        return render_template('product_review.html', products=live_products)
    except Exception:
        return render_template('product_review.html', products=[])
