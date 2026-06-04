from flask import render_template, request, jsonify, url_for
from werkzeug.security import generate_password_hash
from apps import db # مفترض وجود اتصال بقاعدة البيانات
from apps.config import constants
# من المفضل استيراد نموذج المورد الخاص بك هنا: from apps.models import Supplier

@admin.route('/add_supplier', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'GET':
        # تمرير الثوابت للقالب
        return render_template('admin/add_supplier.html', 
                               constants=constants, 
                               next_id="001") # هنا يتم استدعاء الدالة لجلب آخر ID

    if request.method == 'POST':
        data = request.get_json()
        
        try:
            # 1. تشفير كلمة المرور قبل الحفظ
            hashed_password = generate_password_hash(data['password'])
            
            # 2. تجهيز البيانات للحفظ (هنا يتم إدخالها في جدول الموردين)
            # new_supplier = Supplier(
            #     username=data['username'],
            #     password=hashed_password,
            #     activity_type=data['activity_type'],
            #     owner_name=data['owner_name'],
            #     identity_type=data['identity_type'],
            #     ...
            # )
            # db.session.add(new_supplier)
            # db.session.commit()
            
            return jsonify({"status": "success", "message": "تمت أرشفة المورد وتشفير بياناته بنجاح"})
            
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400
