from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from core import db
from services.qumra_handler import query_qumra # المحرك السيادي
import os

# 1. إعداد المسار والـ Blueprint
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
admin_bp = Blueprint('admin_panel', __name__, template_folder=template_dir)

# --- معالج السياق لإظهار التنبيهات في الشريط الجانبي ---
@admin_bp.context_processor
def inject_counts():
    from core.models.supplier import Supplier
    try:
        pending_count = Supplier.query.filter_by(is_approved=False).count()
        return dict(pending_suppliers_count=pending_count)
    except:
        return dict(pending_suppliers_count=0)

# 2. لوحة التحكم (الرئيسية)
@admin_bp.route('/', strict_slashes=False)
@login_required
def dashboard():
    from core.models.supplier import Supplier
    from core.models.product import Product
    try:
        s_count = Supplier.query.count()
        p_count = Product.query.count()
        latest_suppliers = Supplier.query.order_by(Supplier.created_at.desc()).limit(5).all()
        return render_template('dashboard.html', s_count=s_count, p_count=p_count, latest_suppliers=latest_suppliers)
    except Exception as e:
        return render_template('dashboard.html', s_count=0, p_count=0)

# 3. بوابة المراجعة والتعميد (جلب المنتجات التي لم تُنشر بعد)
@admin_bp.route('/sync_now', strict_slashes=False)
@login_required
def sync_now():
    from core.models.product import Product
    # جلب المنتجات التي حالتها "pending" فقط لمراجعتها ونشرها
    pending_products = Product.query.filter_by(status='pending').all()
    return render_template('product_review.html', products=pending_products)

# 4. التنفيذ السيادي: النشر المباشر لقمرة (بدون تخزين محلي للصور)
@admin_bp.route('/product/approve/<int:product_id>', methods=['POST'])
@login_required
def approve_product(product_id):
    from core.models.product import Product
    
    product = Product.query.get_or_404(product_id)
    final_price_sar = request.form.get('final_price')

    # بناء طلب النشر المباشر لـ Qumra GraphQL
    mutation = """
    mutation CreateProduct($input: ProductInput!) {
      productCreate(input: $input) {
        product { id name }
        userErrors { field message }
      }
    }
    """
    
    # تجهيز البيانات للإرسال الفوري (Payload)
    # لاحظ أننا نرسل النصوص والروابط مباشرة من ذاكرة السيرفر لقمرة
    variables = {
        "input": {
            "name": product.name,
            "descriptionHtml": product.description,
            "collections": [product.q_collection_id],
            "variants": [{
                "price": float(final_price_sar),
                "inventoryQuantity": 10
            }],
            # إذا كانت هناك صور، تُرسل كروابط مباشرة لقمرة
            # "images": [{"src": link} for link in product.images_links] 
        }
    }

    try:
        result = query_qumra(mutation, variables)
        
        if result and 'data' in result and not result['data']['productCreate']['userErrors']:
            # بمجرد النجاح، نحذف "أثر" المنتج المحلي أو نكتفي بتغيير حالته
            # ليبقى النظام خفيفاً جداً كما طلبت
            product.q_product_id = result['data']['productCreate']['product']['id']
            product.status = 'active'
            product.is_synced = True
            db.session.commit()
            
            flash(f'✅ تم النشر في سحابة قمرة بنجاح. معرف المنتج: {product.q_product_id}', 'success')
        else:
            error = result['data']['productCreate']['userErrors'][0]['message'] if result else "خطأ اتصال"
            flash(f'❌ فشل النشر: {error}', 'danger')
            
    except Exception as e:
        db.session.rollback()
        flash(f'⚠️ خطأ تقني: {str(e)}', 'danger')

    return redirect(url_for('admin_panel.sync_now'))

# 5. تسجيل الدخول السيادي
@admin_bp.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_panel.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        from core.models.user import User
        user = User.query.filter_by(username=username).first()

        if user and user.password == password: 
            session['user_type'] = 'admin'
            login_user(user)
            flash('أهلاً بك أيها القائد في برج الرقابة', 'success')
            return redirect(url_for('admin_panel.dashboard'))
        else:
            flash('بيانات الولوج غير صحيحة', 'danger')
            
    return render_template('login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    session.pop('user_type', None)
    logout_user()
    return redirect(url_for('admin_panel.login'))
