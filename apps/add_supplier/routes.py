from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from models.supplier_db import db, Supplier

# تعريف الـ Blueprint
add_supplier_bp = Blueprint(
    'add_supplier', 
    __name__, 
    template_folder='templates'
)

# دالة موحدة لعرض الصفحة (GET) ومعالجة الحفظ (POST) لضمان السيادة البرمجية
@add_supplier_bp.route('/admin/supplier/save', methods=['GET', 'POST'])
def save_supplier():
    # التحقق من هوية المؤسس قبل أي إجراء
    if not session.get('is_authenticated'):
        return redirect(url_for('auth.login'))

    # --- أولاً: حالة العرض (GET) ---
    if request.method == 'GET':
        # حساب المعرف القادم لإظهاره في الواجهة (SUP-MHA_963X)
        last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        next_id_count = (last_supplier.id + 1) if last_supplier else 1
        
        # استدعاء قالب لوحة التحكم المخصص للإضافة
        return render_template('admin/dashboard_content.html', next_id=next_id_count)

    # --- ثانياً: حالة الحفظ (POST) ---
    if request.method == 'POST':
        # استقبال البيانات سواء كانت JSON أو Form Data
        data = request.get_json() if request.is_json else request.form
        
        if not data:
            return jsonify({'status': 'error', 'message': 'بيانات المورد مفقودة'}), 400

        try:
            # 1. إنشاء كائن المورد الجديد بربطه بالموديل المعتمد في Postgres
            new_supplier = Supplier(
                username=data.get('username'),
                password=data.get('password'), # ننصح بالتشفير مستقبلاً
                trade_name=data.get('trade_name'),
                owner_name=data.get('owner_name'),
                phone=data.get('phone'),
                activity_type=data.get('activity_type'),
                province=data.get('province'),
                district=data.get('district'),
                address_detail=data.get('address_detail'),
                bank_name=data.get('bank_name'),
                bank_acc=data.get('bank_acc')
            )

            # 2. توليد المعرف السيادي (Sovereign ID) تلقائياً
            count = Supplier.query.count() + 1
            new_supplier.sovereign_id = f"SUP-MHA_963{count}"

            # 3. التنفيذ الفوري والحفظ في قاعدة البيانات
            db.session.add(new_supplier)
            db.session.commit()

            # الاستجابة حسب نوع الطلب (AJAX أو Form)
            if request.is_json:
                return jsonify({
                    'status': 'success', 
                    'message': f'تم تعميد المورد بنجاح بالرقم: {new_supplier.sovereign_id}'
                })
            else:
                flash(f'تم حفظ المورد {new_supplier.trade_name} بنجاح.', 'success')
                return redirect(url_for('admin.dashboard'))

        except Exception as e:
            db.session.rollback() # التراجع في حال حدوث خطأ لمنع تضرر القاعدة
            error_msg = f'فشلت عملية الأرشفة: {str(e)}'
            if request.is_json:
                return jsonify({'status': 'error', 'message': error_msg}), 500
            else:
                flash(error_msg, 'danger')
                return redirect(url_for('add_supplier.save_supplier'))
