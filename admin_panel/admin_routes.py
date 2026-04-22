from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
# نفترض أن اسم الموديل الخاص بك هو User في ملف models
from .models import User 

# تعريف الـ Blueprint الخاص بالإدارة
admin_bp = Blueprint('admin', __name__, template_folder='templates')

# 1. مسار تسجيل الدخول (بوابة الدخول)
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # استقبال البيانات (اسم المستخدم بالعربي: علي محجوب)
        username = request.form.get('username')
        password = request.form.get('password')

        # البحث عن القائد في قاعدة البيانات
        user = User.query.filter_by(username=username).first()

        # التحقق من الهوية وكلمة المرور المشفرة
        if user and check_password_hash(user.password, password):
            login_user(user) # تفعيل الجلسة الآمنة
            flash('مرحباً بك يا قائد، تم الدخول إلى برج الرقابة بنجاح', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('بيانات الدخول غير صحيحة، الوصول مرفوض', 'danger')
            
    return render_template('login.html')

# 2. لوحة الإحصائيات (محمية بـ login_required)
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# 3. مراجعة منتجات المورد (محطة العبور اللحظية)
@admin_bp.route('/product-review')
@login_required
def product_review():
    # هنا سيتم لاحقاً جلب البيانات لحظياً من قمرة دون حفظها
    return render_template('product_review.html')

# 4. إدارة المحافظ المالية
@admin_bp.route('/wallets')
@login_required
def wallets():
    return render_template('wallets.html')

# 5. تسجيل الخروج الآمن
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user() # تدمير الجلسة
    flash('تم تسجيل الخروج وإغلاق بوابة العبور بنجاح', 'info')
    return redirect(url_for('admin.login'))
