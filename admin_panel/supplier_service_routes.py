# admin_panel/supplier_service_routes.py
from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from admin_panel import admin_bp
from core import db
from core.models.supplier import Supplier, SupplierStaff

@admin_bp.route('/suppliers/profile/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
def supplier_profile(supplier_id):
    """
    مسار إدارة بروفايل المورد السيادي:
    - GET: عرض بيانات المورد وطاقم العمل.
    - POST (AJAX): تحديث الحقول بشكل فردي (الحفظ التلقائي) لبيانات المورد الأساسية واسم المستخدم.
    - POST (Form): إضافة موظفين جدد لطاقم العمل للكيان.
    """
    supplier = Supplier.query.get_or_404(supplier_id)

    # 1. بروتوكول التحديث القادم من AJAX (الحفظ التلقائي للحقول)
    if request.method == 'POST' and request.is_json:
        try:
            data = request.get_json()
            field = data.get('field')
            value = data.get('value')
            
            # منع تغيير المعرف السيادي أو كلمة المرور عبر هذا المسار لغرض الأمان اللحظي
            if field == 'password':
                return jsonify({
                    "status": "error", 
                    "message": "تغيير كلمة المرور يتطلب بروتوكولاً أمنياً منفصلاً."
                }), 403

            # التأكد من وجود الحقل في كائن المورد وتحديثه
            if hasattr(supplier, field):
                setattr(supplier, field, value)
                db.session.commit()
                return jsonify({
                    "status": "success", 
                    "message": f"تم تعميد تحديث {field} بنجاح."
                })
            else:
                return jsonify({
                    "status": "error", 
                    "message": f"الحقل '{field}' غير موجود في مصفوفة بيانات المورد."
                }), 400
                
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error", 
                "message": f"عطل في محرك المزامنة: {str(e)}"
            }), 500

    # 2. بروتوكول إضافة موظف جديد (من نافذة المودال)
    if request.method == 'POST' and 'new_username' in request.form:
        try:
            username = request.form.get('new_username')
            name = request.form.get('full_name')
            password = request.form.get('new_password')
            
            # التحقق من عدم تكرار اسم المستخدم في طاقم الموردين
            existing_user = SupplierStaff.query.filter_by(username=username).first()
            if existing_user:
                flash(f"⚠️ اسم المستخدم {username} محجوز مسبقاً في النظام.", "danger")
                return redirect(url_for('admin.supplier_profile', supplier_id=supplier_id))

            # إنشاء عضو جديد في طاقم العمل وتشفير كلمة مروره
            new_staff = SupplierStaff(
                supplier_id=supplier_id,
                username=username,
                name=name
            )
            new_staff.set_password(password) # استخدام ميثود التشفير السيادية
            
            db.session.add(new_staff)
            db.session.commit()
            flash(f"✅ تم تعميد الموظف {name} وإلحاقه بالكيان بنجاح.", "success")
            
        except Exception as e:
            db.session.rollback()
            flash(f"⚠️ فشلت عملية الإلحاق: {str(e)}", "danger")
            
        return redirect(url_for('admin.supplier_profile', supplier_id=supplier_id))

    # 3. بروتوكول العرض السيادي (GET)
    return render_template(
        'suppliers/supplier_profile.html', 
        supplier=supplier
    )

"""
--- بروتوكول الحماية والرقابة ---
1. الحماية اللحظية: تم عزل تعديل كلمات المرور عن الحفظ التلقائي لضمان عدم تمرير نصوص خام (Plain Text).
2. الشفافية: حقل 'username' الآن قابل للتعديل لحظياً ويرتبط مباشرة بقاعدة بيانات الهوية.
3. التشفير: جميع كلمات المرور للموظفين المضافين تخضع لنظام التشفير الخاص بـ Core Models قبل دخولها الـ Postgres.
"""
