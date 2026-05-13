from flask import Blueprint, render_template, request, jsonify
from models.supplier_db import db, Supplier
from datetime import datetime

admin_suppliers = Blueprint('admin_suppliers', __name__, template_folder='templates')

@admin_suppliers.route('/add-supplier', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        # استقبال البيانات بصيغة JSON لمتوافقة مع الجافا سكريبت في قالبك
        data = request.get_json() if request.is_json else request.form
        
        try:
            # ربط البيانات بالحقول الصحيحة في الموديل الخاص بك
            new_supplier = Supplier(
                username=data.get('username'),
                password=data.get('password', '123456'),  # كلمة السر الافتراضية
                email=data.get('email'),
                activity_type=data.get('activity_type'),
                owner_name=data.get('owner_name'),
                identity_type=data.get('identity_type'),
                trade_name=data.get('trade_name'),
                phone=data.get('phone'),
                bank_name=data.get('bank_name'),
                bank_acc=data.get('bank_acc'),
                province=data.get('province'),
                district=data.get('district'),
                address_detail=data.get('address_detail'),
                # توليد المعرف السيادي تلقائياً أو استقباله
                sovereign_id=f"SUP-MHA-{datetime.now().strftime('%y%m%d%H%M')}",
                created_at=datetime.utcnow()
            )
            
            db.session.add(new_supplier)
            db.session.commit()
            
            return jsonify({
                "status": "success", 
                "message": f"تم تعميد المورد {data.get('trade_name')} بنجاح في نظام محجوب أونلاين."
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": f"فشل في الأرشفة: {str(e)}"}), 500

    # في حالة GET، نعرض واجهة التعميد
    return render_template('admin/add_supplier.html')
