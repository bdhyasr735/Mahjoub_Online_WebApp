# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models.supplier_db import db, Supplier  
from datetime import datetime
from functools import wraps

# تعريف الـ Blueprint المركزي للوحة التحكم
admin_bp = Blueprint('admin_dashboard', __name__, template_folder='templates')

def login_required(f):
    """مغلف التحقق من الهوية السيادية لضمان أمن المنظومة"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            # في حال عدم وجود جلسة، يتم التوجيه لصفحة الدخول
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """
    عرض لوحة التحكم الرئيسية
    المسار: /admin/dashboard
    """
    return render_template('admin/dashboard_content.html')

@admin_bp.route('/add-supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    """
    واجهة تعميد وإضافة الموردين الجدد للمنظومة
    المسار: /admin/add-supplier
    """
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form

        try:
            # صياغة بيانات المورد الجديد وفقاً للموديل المعتمد
            new_supplier = Supplier(
                username=data.get('username'),
                password=data.get('password', '123456'), # كلمة مرور افتراضية
                trade_name=data.get('trade_name'),
                owner_name=data.get('owner_name'),
                activity_type=data.get('activity_type'),
                phone=data.get('phone'),
                bank_name=data.get('bank_name'),
                bank_acc=data.get('bank_acc'),
                province=data.get('province'),
                district=data.get('district'),
                address_detail=data.get('address_detail'),
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
            return jsonify({"status": "error", "message": f"عطل فني أثناء الأرشفة: {str(e)}"}), 500

    # التعديل الحاسم هنا: بما أن الملف في مجلد مستقل، نستخدم المسار النسبي أو الكامل
    # Flask سيبحث في كافة مجلدات templates المسجلة في الـ Blueprints
    return render_template('admin/add_supplier.html', next_id=963)

@admin_bp.route('/suppliers-list')
@login_required
def list_suppliers():
    """عرض سجل الموردين المعتمدين في المنظومة"""
    suppliers = Supplier.query.order_by(Supplier.created_at.desc()).all()
    return render_template('admin/list_suppliers.html', suppliers=suppliers)
