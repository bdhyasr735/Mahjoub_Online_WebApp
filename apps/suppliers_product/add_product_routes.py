# apps/suppliers_product/add_product_routes.py

import os
import uuid
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename

# تعريف الـ Blueprint الخاص بإضافة المنتجات
add_product_bp = Blueprint('add_product_bp', __name__, template_folder='templates')

# الامتدادات المسموح بها للصور
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@add_product_bp.route('/add', methods=['GET'])
def add_product_page():
    """عرض صفحة إضافة منتج جديد"""
    try:
        return render_template('suppliers/add_product.html')
    except Exception as e:
        current_app.logger.error(f"خطأ في تحميل صفحة إضافة المنتج: {str(e)}")
        flash('حدث خطأ أثناء تحميل الصفحة', 'danger')
        return redirect(url_for('suppliers_product_bp.products'))

@add_product_bp.route('/api/add', methods=['POST'])
def api_add_product():
    """معالجة طلب إضافة منتج جديد (دعم AJAX والنموذج العادي)"""
    try:
        # استلام البيانات من الطلب (FormData)
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price')
        quantity = request.form.get('quantity', 0)
        sku = request.form.get('sku', '').strip()
        weight = request.form.get('weight', 0)
        status = request.form.get('status', 'DRAFT')

        # التحقق من الحقول الإلزامية
        if not title:
            return jsonify({'success': False, 'message': 'اسم المنتج مطلوب'}), 400
        
        if price is None or price == '':
            return jsonify({'success': False, 'message': 'سعر المنتج مطلوب'}), 400

        try:
            price = float(price)
            if price < 0:
                raise ValueError()
        except ValueError:
            return jsonify({'success': False, 'message': 'سعر المنتج غير صالح'}), 400

        try:
            quantity = int(quantity) if quantity else 0
        except ValueError:
            quantity = 0

        try:
            weight = float(weight) if weight else 0.0
        except ValueError:
            weight = 0.0

        # توليد معرف فريد للمنتج (QID) أو SKU افتراضي إذا لم يوجد
        prod_qid = f"PROD_{uuid.uuid4().hex[:8].upper()}"
        if not sku:
            sku = f"SKU_{uuid.uuid4().hex[:6].upper()}"

        # معالجة رفع الصورة إن وجدت
        image_url = ''
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    ext = filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"{uuid.uuid4().hex}.{ext}"
                    
                    # تحديد مسار حفظ الصور في مجلد المشروع
                    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    file_path = os.path.join(upload_folder, unique_filename)
                    file.save(file_path)
                    
                    # رابط الصورة النسبي
                    image_url = f"/static/uploads/products/{unique_filename}"
                else:
                    return jsonify({'success': False, 'message': 'نوع الملف غير مدعوم. يرجى رفع صورة صالحة'}), 400

        # بناء كائن المنتج الجديد
        new_product = {
            "qid": prod_qid,
            "name": title,
            "description": description,
            "price": price,
            "quantity": quantity,
            "sku": sku,
            "weight": weight,
            "status": status,
            "images": [{"url": image_url}] if image_url else []
        }

        # تسجيل العمليات في السجلات
        current_app.logger.info(f"تم إضافة المنتج بنجاح: {prod_qid} - {title}")

        return jsonify({
            'success': True,
            'message': 'تم إضافة المنتج بنجاح',
            'product': new_product
        }), 200

    except Exception as e:
        current_app.logger.error(f"خطأ أثناء إضافة المنتج: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'حدث خطأ غير متوقع في الخادم: {str(e)}'
        }), 500
