# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, session, url_for, redirect, flash
from flask_login import login_user, logout_user, login_required
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff

# تأكد أن اسم الـ Blueprint هنا هو 'suppliers_auth'
suppliers_bp = Blueprint('suppliers_auth', __name__, template_folder='templates')

@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('suppliers_auth_portal/login.html')

    try:
        data = request.get_json() or request.form.to_dict()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        # تحديد المسار الهدف
        dashboard_url = '/supplier/dashboard' 
        try:
            dashboard_url = url_for('suppliers_dashboard.dashboard')
        except Exception as e:
            print(f"⚠️ [Login Warning]: فشل استدعاء url_for لـ suppliers_dashboard: {e}")

        # 1. محاولة البحث في المورد الرئيسي (الشريك)
        user = Supplier.query.filter(
            (Supplier.search_phone == username) | (Supplier.username == username)
        ).first()
        
        if user and user.check_password(password):
            session.clear()  # تنظيف الجلسة قبل تسجيل دخول جديد
            session['user_type'] = 'supplier'
            session.permanent = True
            login_user(user, remember=True)
            session.modified = True
            return jsonify({"status": "success", "redirect": dashboard_url})

        # 2. البحث في جدول الموظفين
        staff = SupplierStaff.query.filter(
            (SupplierStaff.phone == username) | (SupplierStaff.username == username)
        ).first()

        if staff and staff.check_password(password):
            # فحص إضافي لحالة الحساب قبل السماح بالدخول
            if not getattr(staff, 'is_active', True):
                return jsonify({"status": "error", "message": "حسابك معطل، يرجى مراجعة الشريك"}), 403
            
            session.clear()  # تنظيف الجلسة قبل تسجيل دخول الموظف
            session['user_type'] = 'staff'
            session.permanent = True
            login_user(staff, remember=True)
            session.modified = True # إجبار Flask على حفظ بيانات الجلسة
            return jsonify({"status": "success", "redirect": dashboard_url})

        return jsonify({"status": "error", "message": "بيانات الدخول غير صحيحة"}), 401

    except Exception as e:
        print(f"❌ [Login Error]: {str(e)}")
        return jsonify({"status": "error", "message": f"حدث خطأ في النظام: {str(e)}"}), 500

@suppliers_bp.route('/logout')
@login_required
def logout():
    session.clear()  # مسح كامل للجلسة عند الخروج
    logout_user()
    return redirect(url_for('suppliers_auth.login'))
