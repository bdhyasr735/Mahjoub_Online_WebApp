# coding: utf-8
# 📂 apps/mahjoub_bridge/routes.py

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from apps import db
from apps.models.bridge_db import Product
from apps.utils.bridge_engine import QumraBridgeEngine
import traceback

bridge_bp = Blueprint('mahjoub_bridge', __name__, template_folder='templates')

@bridge_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """عرض لوحة التحكم مع المنتجات الموجودة في القاعدة."""
    page = request.args.get('page', 1, type=int)
    per_page = 16
    
    # جلب المنتجات من قاعدة البيانات المحلية مباشرة
    pagination = Product.query.order_by(Product.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items
    
    return render_template('admin/bridge_dashboard.html', 
                           products=products, 
                           pagination=pagination)

@bridge_bp.route('/sync-now', methods=['POST'])
def sync_now():
    """المزامنة اللحظية مع المحرك وحفظ البيانات."""
    try:
        engine = QumraBridgeEngine()
        # جلب البيانات من المحرك
        raw_products = engine.fetch_latest_products(limit=50)
        
        if not raw_products:
            return jsonify({"status": "error", "message": "لم يتم العثور على منتجات في السيرفر"})

        count = 0
        for item in raw_products:
            # التحقق من وجود العنوان
            title = str(item.get('title') or "منتج بدون اسم").strip()
            
            # منع التكرار
            if Product.query.filter_by(title=title).first():
                continue
            
            # التعامل مع السعر والكمية
            pricing = item.get('pricing') or {}
            price = str(pricing.get('price') or "0")
            qty = item.get('quantity') or 0
            img = item.get('image_url') or ""
            
            # إنشاء المنتج
            new_product = Product(
                title=title,
                price=price,
                quantity=int(qty),
                image_url=img,
                supplier_id="QUMRA_SYNC"
            )
            
            # إضافة قالب العرض
            new_product.auto_template = f'<img src="{img}" style="width:50px;height:50px;object-fit:cover;">'
            
            db.session.add(new_product)
            count += 1
        
        db.session.commit()
        return jsonify({"status": "success", "message": f"تمت المزامنة بنجاح وجلب {count} منتج"})
        
    except Exception:
        db.session.rollback()
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": "خطأ أثناء المزامنة"}), 500
