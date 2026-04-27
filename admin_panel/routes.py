from flask import render_template, redirect, url_for, flash, request
from admin_panel import admin_bp

# 1. مسار تسجيل الدخول للإدارة
@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        # جلب البيانات من نموذج الدخول
        username = request.form.get('username')
        password = request.form.get('password')
        
        # التحقق السيادي (بيانات الدخول)
        if username == "ali_admin" and password == "9046":
            return redirect(url_for('admin_panel.admin_dashboard'))
        else:
            flash('فشل التحقق السيادي: بيانات غير صحيحة', 'danger')
            
    # استدعاء القالب من المسار: admin_panel/templates/admin_panel/login.html
    return render_template('admin_panel/login.html')

# 2. لوحة التحكم الرئيسية (برج الرقابة)
@admin_bp.route('/dashboard')
def admin_dashboard():
    # هنا سيتم لاحقاً إضافة الكود الخاص بإحصائيات "سوقك الذكي"
    return """
    <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
        <h1 style="color: #16213e;">🏛️ برج الرقابة المركزية</h1>
        <p>مرحباً بك يا علي.. "سوقك الذكي" الآن تحت السيطرة الكاملة.</p>
        <hr style="width: 50%; border: 1px solid #e94560;">
        <a href="/admin_control_9046/login" style="color: #e94560; text-decoration: none;">تسجيل الخروج</a>
    </div>
    """
