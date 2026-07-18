from flask import render_template, request, jsonify, redirect, url_for, flash
from . import admin_product_bp  # افتراض أنك تستخدم Blueprint
# استورد دوال التعامل مع قاعدة البيانات أو الـ API الخاص بـ "قمرة" هنا
# from .models import Product 

@admin_product_bp.route('/add-product', methods=['GET', 'POST'])
def add_product():
    """
    عرض صفحة إضافة منتج جديد ومعالجة بيانات الفورم.
    """
    if request.method == 'GET':
        return render_template('admin/admin_add_product.html')

    if request.method == 'POST':
        try:
            # استلام البيانات من الفرونت إند
            data = request.get_json()
            
            title = data.get('title')
            price = data.get('price')
            quantity = data.get('quantity')
            sku = data.get('sku')
            
            # هنا تضع منطق الإضافة:
            # 1. التحقق من البيانات (Validation)
            if not title or not price:
                return jsonify({'status': 'error', 'message': 'البيانات الأساسية ناقصة'}), 400
            
            # 2. إرسال البيانات لـ "قمرة" أو حفظها في قاعدة بياناتك
            # new_product = save_to_db(title=title, price=price, ...)
            
            print(f"جاري إضافة المنتج: {title}") # للتتبع في السيرفر
            
            return jsonify({
                'status': 'success', 
                'message': 'تم إضافة المنتج بنجاح'
            }), 200
            
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_product_bp.route('/save-sync', methods=['POST'])
def save_sync():
    """
    مسار عام لحفظ التعديلات أو الإضافات الجديدة (يمكن دمجه مع logic التحديث).
    """
    data = request.get_json()
    # هنا يتم التعامل مع منطق المزامنة بعد الإضافة/التعديل
    # ...
    return jsonify({'status': 'success', 'message': 'تمت المزامنة بنجاح'})
