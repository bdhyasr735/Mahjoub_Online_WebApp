# 📂 apps/vendors/routes.py

from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from .vendor_auth_service import vendor_login_required

# تعريف الـ Blueprint للموردين
vendors_bp = Blueprint('vendors', __name__, template_folder='templates')

@vendors_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    """صفحة تسجيل الدخول التي تستقبل بيانات المورد"""
    if request.method == 'POST':
        data = request.get_json()  # استقبال البيانات بصيغة JSON من الـ Frontend
        
        # هنا يجب ربط منطق التحقق من الـ OTP المرسل من login.html
        # 1. التحقق من كود الـ OTP
        # 2. إذا كان صحيحاً:
        session['vendor_authenticated'] = True
        session['vendor_name'] = data.get('username', 'المورد الكريم')
        
        return jsonify({"status": "success", "message": "تم الدخول بنجاح"})
    
    return render_template('vendor/login.html')

@vendors_bp.route('/dashboard')
@vendor_login_required  # حارس المسارات (لا يدخل إلا من تم التحقق منه)
def dashboard():
    """لوحة تحكم المورد (محمية)"""
    return render_template('vendor/dashboard.html', vendor_name=session.get('vendor_name'))

@vendors_bp.route('/logout')
def logout():
    """تسجيل الخروج وإنهاء الجلسة"""
    session.clear()
    return redirect(url_for('vendors.login_page'))
