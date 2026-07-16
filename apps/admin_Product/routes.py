# coding: utf-8
# 📂 apps/admin_Product/routes.py

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from apps.models.product_db import Product
from apps.extensions import db
from apps.services.graphql_client import QomrahGraphQLClient

# تعريف البلوبرنت الخاص بإدارة المنتجات
admin_product_bp = Blueprint(
    'admin_product_bp', 
    __name__, 
    template_folder='templates'
)

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    """عرض قائمة المنتجات مع نظام التصفح"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = Product.query.order_by(Product.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template(
        'admin/admin_Product.html', 
        products=pagination.items,
        pagination=pagination
    )

@admin_product_bp.route('/proxy-sync', methods=['POST'])
@login_required
def proxy_sync():
    """الوكيل (Proxy) لجلب البيانات من قمرة عبر GraphQL"""
    
    # بناءً على الخطأ، الـ API لا يقبل (page, limit) ولا يعرف الـ items
    # تم تعديل الاستعلام ليكون أبسط. إذا فشل هذا، سنحتاج لاستخدام الاستعلام الاستكشافي.
    query = """
    query { 
        findAllProducts { 
            _id 
            title 
            price 
            sku 
        } 
    }
    """
    
    # تنفيذ الاستعلام
    data = QomrahGraphQLClient.execute_query(query)
    
    if data is None:
        return jsonify({
            "status": "error", 
            "message": "فشل الاتصال بخدمة المزامنة. راجع سجلات الأخطاء لمعرفة هيكل البيانات الصحيح."
        }), 500
        
    return jsonify({"status": "success", "data": data})

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    """حفظ البيانات المجلوبة في قاعدة البيانات المحلية"""
    try:
        data = request.json
        # لاحظ: بناءً على الرد، قد تحتاج لتعديل المفتاح هنا إذا كان الـ API يرجع البيانات بشكل مختلف
        products_data = data.get('products', [])
        
        if not products_data:
            return jsonify({"status": "error", "message": "لا توجد منتجات للمزامنة"})

        count = 0
        for item in products_data:
            qid = str(item.get('_id'))
            product = Product.query.filter_by(qid=qid).first()
            
            try:
                price = float(item.get('price', 0))
            except (ValueError, TypeError):
                price = 0.0

            if not product:
                new_product = Product(
                    qid=qid,
                    title=item.get('title', 'منتج غير معرف'),
                    sku=item.get('sku', 'N/A'),
                    cost_price=price
                )
                db.session.add(new_product)
                count += 1
            else:
                product.title = item.get('title', product.title)
                product.cost_price = price
                product.sku = item.get('sku', product.sku)
        
        db.session.commit()
        return jsonify({
            "status": "success", 
            "message": f"تمت المعالجة: إضافة {count} منتج جديد وتحديث المنتجات الحالية."
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"خطأ في حفظ البيانات: {str(e)}"}), 500
