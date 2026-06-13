# coding: utf-8
# 📂 apps/mahjoub_bridge/routes.py

from flask import Blueprint, render_template, request, jsonify
from apps import db
from apps.models.bridge_db import Product
from apps.utils.bridge_engine import QumraBridgeEngine
import traceback

bridge_bp = Blueprint('mahjoub_bridge', __name__, template_folder='templates')

@bridge_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """لوحة التحكم مع دعم البحث والفلترة حسب الحالة."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '', type=str)
    status_filter = request.args.get('status', '', type=str)
    per_page = 16
    
    query = Product.query
    
    if search:
        query = query.filter(Product.title.contains(search))
    
    if status_filter and hasattr(Product, 'status'):
        query = query.filter(Product.status == status_filter)
        
    pagination = query.order_by(Product.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/bridge_dashboard.html', 
                           products=pagination.items, 
                           pagination=pagination,
                           search=search)

@bridge_bp.route('/add', methods=['GET', 'POST'])
def add_product():
    return render_template('admin/add_product.html')

@bridge_bp.route('/sync-now', methods=['POST'])
def sync_now():
    """المزامنة اللحظية مع المحرك وحفظ البيانات."""
    try:
        engine = QumraBridgeEngine()
        # جلب البيانات المعالجة جاهزة من المحرك
        products = engine.fetch_latest_products()
        
        if not products:
            return jsonify({"status": "error", "message": "لم يتم العثور على منتجات لجلبها"})

        count = 0
        for item in products:
            title = str(item.get('title') or "منتج بدون اسم").strip()
            
            # منع التكرار
            if Product.query.filter_by(title=title).first():
                continue
            
            # إنشاء المنتج باستخدام البيانات الجاهزة من المحرك
            new_product = Product(
                title=title,
                price=str(item.get('price') or "0"),
                quantity=int(item.get('quantity') or 0),
                image_url=item.get('image_url'),
                supplier_id="QUMRA_SYNC"
            )
            
            if hasattr(new_product, 'status'):
                new_product.status = item.get('status', 'draft')
            
            db.session.add(new_product)
            count += 1
        
        db.session.commit()
        return jsonify({"status": "success", "message": f"تمت المزامنة بنجاح وجلب {count} منتج جديد"})
        
    except Exception:
        db.session.rollback()
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": "حدث خطأ أثناء معالجة البيانات"}), 500
