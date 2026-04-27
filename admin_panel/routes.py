from flask import render_template, redirect, url_for, flash, request
from admin_panel import admin_bp  # التعديل لضمان الوصول المباشر للبلوبرينت

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        # منطق التحقق من البيانات (اسم المستخدم وكلمة المرور)
        username = request.form.get('username')
        password = request.form.get('password')
        
        # التحقق السيادي للدخول
        if username == "ali_admin" and password == "9046":
            return redirect(url_for('admin_panel.admin_dashboard'))
        else:
            flash('فشل التحقق السيادي: بيانات غير صحيحة', 'danger')
            
    # استدعاء القالب من المسار الذي حددته أنت: admin_panel/templates/admin_panel/login.html
    # Flask سيبحث تلقائياً داخل مجلد templates، لذا نكتب المسار الداخلي فقط
    return render_template('admin_panel/login.html')

@admin_bp.route('/dashboard')
def admin_dashboard():
    return "مرحباً بك في لوحة تحكم محجوب أونلاين - برج الرقابة المركزية"
