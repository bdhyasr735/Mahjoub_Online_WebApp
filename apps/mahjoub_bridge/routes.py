# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from apps import db
from apps.models.bridge_db import Product, ProductVariant
from apps.utils.bridge_engine import QumraBridgeEngine
import traceback

bridge_bp = Blueprint('mahjoub_bridge', __name__, template_folder='templates')

@bridge_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """عرض لوحة التحكم (الموديل يفك التشفير تلقائياً عند قراءة .price)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 16
        pagination = Product.query.order_by(Product.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
        products = pagination.items
        
        return render_template('admin/bridge_dashboard.html', 
                               products=products, 
                               pagination=pagination, 
                               page=page)
                               
    except Exception as e:
        print(f"Error in bridge dashboard: {str(e)}")
        flash(f"حدث خطأ: {str(e)}", "danger")
        return redirect(url_for('admin_dashboard.dashboard'))

@bridge_bp.route('/add-product', methods=['GET', 'POST'])
def add_product_page():
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            if not title:
                flash('عنوان المنتج مطلوب!', 'warning')
                return redirect(url_for('mahjoub_bridge.add_product_page'))
            
            raw_price = request.form.get('price', '0')
            qty = int(request.form.get('quantity', 0))
            
            new_product = Product(
                title=title,
                description=request.form.get('description', ''),
                quantity=qty,
                supplier_id=request.form.get('supplier_id')
            )
            # التشفير يحدث تلقائياً هنا عبر الـ setter في الموديل
            new_product.price = str(raw_price) 
            
            db.session.add(new_product)
            db.session.commit()
            flash('تم إضافة المنتج بنجاح', 'success')
            return redirect(url_for('mahjoub_bridge.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ أثناء الحفظ: {str(e)}', 'danger')
    return render_template('admin/add_product.html')

@bridge_bp.route('/sync-now', methods=['POST'])
def sync_now():
    """المزامنة اللحظية مع الاعتماد على الموديل للتشفير التلقائي"""
    try:
        engine = QumraBridgeEngine()
        raw_products = engine.fetch_latest_products(limit=20)
        
        if not raw_products or not isinstance(raw_products, list):
            return jsonify({"status": "error", "message": "فشل الاتصال بمحرك المزامنة أو لا توجد بيانات"})

        count = 0
        for item in raw_products:
            if not isinstance(item, dict): continue
            
            title = str(item.get('title') or "").strip()
            if not title or Product.query.filter_by(title=title).first():
                continue
            
            pricing = item.get('pricing')
            raw_price = str(pricing.get('price') if isinstance(pricing, dict) else "0")
            
            raw_qty = item.get('quantity')
            safe_qty = int(raw_qty) if str(raw_qty or "").isdigit() else 0
            
            new_product = Product(
                title=title,
                description="تمت المزامنة تلقائياً",
                quantity=safe_qty,
                supplier_id="QUMRA_SYNC"
            )
            # التشفير التلقائي
            new_product.price = raw_price
            
            db.session.add(new_product)
            count += 1
        
        db.session.commit()
        return jsonify({"status": "success", "message": f"تمت المزامنة بنجاح وجلب {count} منتج"})
        
    except Exception as e:
        db.session.rollback()
        print(f"CRITICAL SYNC ERROR: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "حدث خطأ تقني في المزامنة"}), 500
