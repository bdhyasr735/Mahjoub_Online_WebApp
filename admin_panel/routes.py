from flask import Blueprint, render_template, request

# 1. تعريف البلوبرنت وتحديد مجلد القوالب (Templates)
# بما أن الملفات داخل admin_panel/templates، فإن Flask سيجدها تلقائياً
admin_bp = Blueprint('admin_panel', __name__, template_folder='templates')

# 2. مسار لوحة التحكم الرئيسية (Dashboard)
@admin_bp.route('/', strict_slashes=False)
def dashboard():
    # استيراد المودلز هنا يكسر الحلقة الدائرية ويمنع الخطأ الأحمر في Railway
    from core.models import Supplier, Product
    try:
        # جلب الإحصائيات من قاعدة بيانات رندر
        s_count = Supplier.query.count()
        p_count = Product.query.count()
        return render_template('dashboard.html', s_count=s_count, p_count=p_count)
    except Exception as e:
        print(f"⚠️ تنبيه: تعذر جلب البيانات من القاعدة: {e}")
        return render_template('dashboard.html', s_count=0, p_count=0)

# 3. مسار عرض المنتجات اللحظي (المستورد من قمرة)
@admin_bp.route('/sync_now', strict_slashes=False)
def sync_now():
    try:
        # استيراد المحرك هنا يحل مشكلة 'No module named core.qumra_sync'
        from core.qumra_sync import qumra_manager
        live_products = qumra_manager.fetch_live_products(limit=15)
        return render_template('product_review.html', products=live_products)
    except Exception as e:
        print(f"❌ خطأ في محرك المزامنة: {e}")
        return f"خطأ في الاتصال بمحرك المزامنة: {e}"

# 4. مسار قائمة الموردين
@admin_bp.route('/suppliers', strict_slashes=False)
def list_suppliers():
    from core.models import Supplier
    try:
        suppliers = Supplier.query.all()
        return render_template('suppliers_list.html', suppliers=suppliers)
    except Exception:
        return "جاري تهيئة قاعدة بيانات الموردين..."

# 5. مسار الدخول (Login)
@admin_bp.route('/login', strict_slashes=False)
def login():
    return render_template('login.html')
