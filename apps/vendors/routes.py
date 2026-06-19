# 📂 apps/vendors/routes.py
from flask import render_template, request, redirect, url_for, flash
from . import vendors_bp

# مسار بوابة دخول الموردين
@vendors_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # هنا ستضع منطق التحقق الخاص بك لاحقاً
        # مثال: if supplier_auth(username, password):
        #     return redirect(url_for('vendors.dashboard'))
        
        flash("بيانات الدخول غير صحيحة")
        return render_template('vendor/login.html')
        
    return render_template('vendor/login.html')

# مسار لوحة التحكم الخاصة بالمورد
@vendors_bp.route('/dashboard')
def dashboard():
    # هنا يمكنك إضافة حماية للتأكد من تسجيل الدخول (Login Required)
    return render_template('vendor/dashboard.html')
