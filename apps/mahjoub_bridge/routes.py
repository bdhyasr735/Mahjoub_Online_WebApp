# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from apps import db
from apps.models.bridge_db import Product, ProductVariant, encrypt
from apps.utils.bridge_engine import QumraBridgeEngine

bridge_bp = Blueprint('mahjoub_bridge', __name__, template_folder='templates')

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
            # تشفير السعر يدوياً عند الإضافة اليدوية
            raw_price = request.form.get('price', 0)
            encrypted_price = encrypt(raw_price)
            
            qty_raw = request.form.get('quantity', 0)
            
            if not title:
                flash('عنوان المنتج مطلوب!', 'warning')
                return redirect(url_for('mahjoub_bridge.add_product_page'))

            new_product = Product(
                title=title,
                description=request.form.get('description', ''),
                price=encrypted_price, # تخزين مشفر
                quantity=int(qty_raw),
                supplier_id=request.form.get('supplier_id')
            )
            db.session.add(new_product)
            db.session.commit()
            
            flash('تم إضافة المنتج وتشفير بياناته بنجاح', 'success')
            return redirect(url_for('mahjoub_bridge.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ أثناء الحفظ: {str(e)}', 'danger')
    
    return render_template('admin/add_product.html')

@bridge_bp.route('/sync-now', methods=['POST'])
def sync_now():
    """المزامنة اللحظية: جلب البيانات وتخزينها مشفرة"""
    try:
        engine = QumraBridgeEngine()
        raw_products = engine.fetch_latest_products(limit=20)
        
        if not raw_products:
            return jsonify({"status": "warning", "message": "لم يتم العثور على منتجات جديدة أو فشل الاتصال بالـ API"})

        count = 0
        for item in raw_products:
            # التحقق من وجود المنتج
            existing = Product.query.filter_by(title=item.get('title')).first()
            if not existing:
                # استخراج وتشفير السعر
                raw_price = item.get('pricing', {}).get('price', 0)
                
                new_product = Product(
                    title=item.get('title'),
                    description="تمت المزامنة تلقائياً",
                    price=encrypt(raw_price), # تشفير آلي أثناء المزامنة
                    quantity=int(item.get('quantity', 0)),
                    supplier_id="QUMRA_SYNC"
                )
                db.session.add(new_product)
                count += 1
        
        db.session.commit()
        return jsonify({"status": "success", "message": f"تمت المزامنة بنجاح وجلب {count} منتج جديد مشفر"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"فشل المزامنة: {str(e)}"}), 500
