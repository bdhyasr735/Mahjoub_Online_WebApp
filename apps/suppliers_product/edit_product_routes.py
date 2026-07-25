# apps/suppliers_product/edit_product_routes.py

import os
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename

# تعريف الـ Blueprint الخاص بتعديل المنتجات
edit_product_bp = Blueprint(
    'edit_product_bp',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# امتدادات الصور المسموح برفعها
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@edit_product_bp.route('/products/edit/<qid>', methods=['GET'])
def edit_product_page(qid):
    """
    عرض صفحة تعديل المنتج باستخدام معرف المنتج (qid)
    """
    try:
        # TODO: جلب بيانات المنتج الفعلية عبر خدمة البيانات أو استعلام GraphQL باستخدام qid
        # product_data = fetch_product_by_qid(qid)
        
        return render_template('suppliers/edit_product.html', product={'qid': qid})
    except Exception as e:
        current_app.logger.error(f"Error loading edit product page for {qid}: {str(e)}")
        return render_template('suppliers/edit_product.html', product={'qid': qid}, error=str(e))


@edit_product_bp.route('/api/products/<qid>', methods=['PUT'])
def api_update_product(qid):
    """
    معالجة طلب التحديث (PUT) القادم من الواجهة عبر AJAX وتحديث بيانات المنتج
    """
    try:
        # استلام البيانات المرسلة عبر FormData
        title = request.form.get('title')
        description = request.form.get('description', '')
        price = request.form.get('price')
        quantity = request.form.get('quantity', 0)
        sku = request.form.get('sku', '')
        weight = request.form.get('weight', 0.0)
        status = request.form.get('status', 'DRAFT')
        current_image_id = request.form.get('current_image_id', '')

        # التحقق من صحة المدخلات الأساسية
        if not title or not price:
            return jsonify({
                'success': False,
                'message': 'اسم المنتج والسعر الحقلان الأساسيان مطلوبان.'
            }), 400

        try:
            price = float(price)
            quantity = int(quantity) if quantity != '' else 0
            weight = float(weight) if weight != '' else 0.0
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'قيم السعر أو الكمية أو الوزن غير صالحة.'
            }), 400

        # معالجة رفع الصورة الجديدة إن وجدت
        image_file = request.files.get('image')
        image_url = None
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            image_file.save(file_path)
            image_url = f"/static/uploads/{filename}"

        # تجهيز هيكل البيانات لتنفيذ التحديث (Mutation عبر GraphQL أو حفظ مباشر)
        update_payload = {
            'qid': qid,
            'title': title,
            'description': description,
            'price': price,
            'quantity': quantity,
            'sku': sku,
            'weight': weight,
            'status': status,
            'current_image_id': current_image_id
        }
        
        if image_url:
            update_payload['imageUrl'] = image_url

        # TODO: تنفيذ استعلام GraphQL Mutation لتحديث المنتج في النظام الخلفي
        # response_data = execute_graphql_mutation(update_payload)

        current_app.logger.info(f"Product {qid} successfully updated with payload: {update_payload}")

        return jsonify({
            'success': True,
            'message': 'تم تحديث بيانات المنتج بنجاح',
            'data': update_payload
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error updating product {qid}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'حدث خطأ داخلي أثناء تحديث المنتج: {str(e)}'
        }), 500
