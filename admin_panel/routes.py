from flask import Blueprint, render_template, request

# 1. تعريف البلوبرنت
admin_bp = Blueprint('admin_panel', __name__, template_folder='templates')

# 2. مسار لوحة التحكم (Dashboard)
@admin_bp.route('/', strict_slashes=False)
def dashboard():
    # استيراد المودلز هنا يكسر الحلقة الدائرية (Circular Import)
    from core.models import Supplier, Product
    try:
        s_count = Supplier.query.count()
        p_count = Product.query.count()
        return render_template('dashboard.html', s_count=s_count, p_count=p_count)
    except Exception:
        return render_template('dashboard.html', s_count=0, p_count=0)

# 3. مسار عرض المنتجات (الذي صممناه)
@admin_bp.route('/sync_now', strict_slashes=False)
def sync_now():
    # استيراد المحرك هنا يحل مشكلة (No module named core.qumra_sync)
    try:
        from core.qumra_sync import qumra_manager
        live_products = qumra_manager.fetch_live_products(limit=15)
        return render_template('product_review.html', products=live_products)
    except ImportError:
        return "⚠️ خطأ: تأكد من وجود ملف core/qumra_sync.py"

# 4. مسار الدخول (Login)
@admin_bp.route('/login', strict_slashes=False)
def login():
    return render_template('login.html')
