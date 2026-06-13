# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from apps import db
from apps.models.bridge_db import Product, ProductVariant, encrypt, decrypt
from apps.utils.bridge_engine import QumraBridgeEngine
import traceback

bridge_bp = Blueprint('mahjoub_bridge', __name__, template_folder='templates')

@bridge_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """عرض لوحة التحكم مع تأمين فك التشفير"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 16
        pagination = Product.query.order_by(Product.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
        products = pagination.items
        
        def safe_decrypt(value):
            if not value: return "0.00"
            try:
                return decrypt(value)
            except:
                return "0.00"

        return render_template('admin/bridge_dashboard.html', 
                               products=products, 
                               pagination=pagination, 
                               page=page, 
                               decrypt=safe_decrypt)
                               
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
            encrypted_price = encrypt(str(raw_price))
            qty = int(request.form.get('quantity', 0))
            
            new_product = Product(
                title=title,
                description=request.form.get('description', ''),
                price=encrypted_price,
                quantity=qty,
                supplier_id=request.form.get('supplier_id')
            )
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
    """المزامنة اللحظية مع حماية قصوى ضد البيانات الفارغة أو المعطوبة"""
    try:
        engine = QumraBridgeEngine()
        raw_products = engine.fetch_latest_products(limit=20)
        
        # DEBUG: للتحقق من وصول البيانات
        print(f"DEBUG: raw_products content is: {raw_products}")
        
        # حماية صارمة ضد الـ None والأنواع غير المتوقعة
        if not raw_products or not isinstance(raw_products, list):
            return jsonify({"status": "error", "message": "فشل الاتصال بمحرك المزامنة أو لا توجد بيانات"})

        count = 0
        for item in raw_products:
            # تخطي أي عنصر ليس قاموساً
            if not isinstance(item, dict):
                continue
            
            # استخراج العنوان بأمان
            title_raw = item.get('title')
            if not title_raw:
                continue
            title = str(title_raw).strip()
            
            # التحقق من عدم التكرار (لتوفير موارد السيرفر)
            if Product.query.filter_by(title=title).first():
                continue
            
            # تنظيف السعر: التأكد أن pricing قاموس قبل المعالجة
            pricing = item.get('pricing')
            raw_price = "0"
            if isinstance(pricing, dict):
                raw_price = str(pricing.get('price') or "0")
            
            # تنظيف الكمية
            raw_qty = item.get('quantity')
            safe_qty = int(raw_qty) if str(raw_qty or "").isdigit() else 0
            
            new_product = Product(
                title=title,
                description="تمت المزامنة تلقائياً",
                price=encrypt(raw_price),
                quantity=safe_qty,
                supplier_id="QUMRA_SYNC"
            )
            db.session.add(new_product)
            count += 1
        
        db.session.commit()
        return jsonify({"status": "success", "message": f"تمت المزامنة بنجاح وجلب {count} منتج"})
        
    except Exception as e:
        db.session.rollback()
        # طباعة تفاصيل الخطأ في الـ Logs لتسهيل التشخيص
        print(f"CRITICAL SYNC ERROR: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "حدث خطأ تقني في معالجة بيانات المزامنة"}), 500
