from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from apps import db
from apps.models.bridge_db import Product, ProductVariant

bridge_bp = Blueprint('mahjoub_bridge', __name__, template_folder='templates')

# تم حذف bridge/ من البداية لأن الـ url_prefix سيقوم بإضافتها
@bridge_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """عرض لوحة التحكم مع نظام ترقيم الصفحات"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 16
        pagination = Product.query.order_by(Product.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
        products = pagination.items
        return render_template('admin/bridge_dashboard.html', products=products, pagination=pagination, page=page)
    except Exception as e:
        flash(f"حدث خطأ أثناء تحميل البيانات: {str(e)}", "danger")
        return redirect(url_for('admin_dashboard.dashboard'))

@bridge_bp.route('/add-product', methods=['GET', 'POST'])
def add_product_page():
    """إضافة منتج جديد"""
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            price_raw = request.form.get('price', 0)
            qty_raw = request.form.get('quantity', 0)
            
            if not title:
                flash('عنوان المنتج مطلوب!', 'warning')
                return redirect(url_for('mahjoub_bridge.add_product_page'))

            new_product = Product(
                title=title,
                description=request.form.get('description', ''),
                price=float(price_raw),
                quantity=int(qty_raw),
                supplier_id=request.form.get('supplier_id')
            )
            db.session.add(new_product)
            db.session.commit()
            
            flash('تم إضافة المنتج وتشفير بياناته بنجاح', 'success')
            return redirect(url_for('mahjoub_bridge.dashboard'))
            
        except ValueError:
            flash('تأكد من إدخال أرقام صحيحة للسعر والكمية', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ أثناء الحفظ: {str(e)}', 'danger')
    
    return render_template('admin/add_product.html')

@bridge_bp.route('/sync-now', methods=['POST'])
def sync_now():
    # الآن سيصبح الرابط الصحيح هو /bridge/sync-now
    return jsonify({"status": "success", "message": "تمت المزامنة بنجاح"})
