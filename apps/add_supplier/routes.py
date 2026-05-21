# coding: utf-8
# ⚙️ محرك تعميد وإدارة الموردين - منصة محجوب أونلاين 2026

from flask import render_template, request, jsonify, url_for
from flask_login import login_required
from . import admin_suppliers_bp
from apps.models.supplier_db import Supplier, db
# تأكد من استيراد نموذج المحفظة إذا كنت تنشئها في نفس الوقت
from apps.models.wallet_db import SupplierWallet 

@admin_suppliers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier_submit():
    """
    مسار تعميد مورد جديد - معالجة نموذج التقديم
    """
    if request.method == 'POST':
        try:
            # 1. استلام البيانات من النموذج
            username = request.form.get('username')
            password = request.form.get('password') # ملاحظة: يفضل تشفيره قبل الحفظ
            owner_name = request.form.get('owner_name')
            trade_name = request.form.get('trade_name')
            owner_phone = request.form.get('owner_phone')
            
            # 2. توليد المعرفات (يجب أن تتطابق مع التنسيق في الواجهة)
            # افترضنا هنا توليدها بناءً على منطق بسيط أو تسلسلي
            new_sup_id = "SUP-MAH9631" 
            new_wal_id = "WEL-MAH9631"

            # 3. حفظ البيانات في قاعدة البيانات
            new_supplier = Supplier(
                username=username,
                owner_name=owner_name,
                trade_name=trade_name,
                sovereign_id=new_sup_id
            )
            db.session.add(new_supplier)
            
            # إنشاء محفظة افتراضية للمورد
            new_wallet = SupplierWallet(
                supplier_id=new_sup_id,
                wallet_code=new_wal_id
            )
            db.session.add(new_wallet)
            
            db.session.commit()

            # 4. إرجاع استجابة JSON للـ JavaScript
            return jsonify({
                "status": "success",
                "message": "تم تعميد المورد بنجاح",
                "data": {
                    "sovereign_id": new_sup_id,
                    "wallet_code": new_wal_id
                }
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500

    return render_template('add_supplier/add_supplier.html')

@admin_suppliers_bp.route('/list', methods=['GET'])
@login_required
def list_suppliers_data():
    suppliers = Supplier.query.all()
    return render_template('add_supplier/list.html', suppliers=suppliers)

# لتفادي خطأ Could not build url
add_supplier_route = add_supplier_submit
