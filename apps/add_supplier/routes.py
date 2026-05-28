# coding: utf-8
# 🛡️ معالج الموردين - منصة محجوب أونلاين 2026

from flask import Blueprint, render_template, request, jsonify

# تعريف البلوبرينت
add_supplier = Blueprint('add_supplier', __name__, template_folder='templates')

@add_supplier.route('/add_supplier', methods=['GET'])
def add_supplier_page():
    """عرض نموذج تعميد المورد - تم تحديث مسار القالب ليتوافق مع add_supplier.html"""
    return render_template('admin/add_supplier.html')

@add_supplier.route('/add_supplier_submit', methods=['POST'])
def add_supplier_submit():
    """استلام ومعالجة البيانات"""
    try:
        # استلام البيانات من النموذج
        # تأكد من أن حقل 'full_encrypted_data' موجود في النموذج في ملف HTML
        data = request.form.get('full_encrypted_data')
        
        if not data:
            return jsonify({"status": "error", "message": "لم يتم استلام بيانات"}), 400

        # Debug log للتحقق من وصول البيانات
        print(f"DEBUG: Data Received: {data}")

        return jsonify({
            "status": "success", 
            "message": "تم استلام طلب تعميد المورد بنجاح، سيتم معالجة البيانات."
        })

    except Exception as e:
        print(f"❌ خطأ في معالجة طلب المورد: {e}")
        return jsonify({"status": "error", "message": "حدث خطأ داخلي في المعالجة"}), 500
