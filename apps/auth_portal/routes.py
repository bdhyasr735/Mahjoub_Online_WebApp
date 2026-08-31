from flask import Blueprint, request, jsonify, url_for, session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

auth_portal_bp = Blueprint('auth_portal_bp', __name__, template_folder='templates')

@auth_portal_bp.route('/login', methods=['GET', 'POST'])
def login():
    """معالجة تسجيل الدخول للمشرفين (تدعم عرض الصفحة GET ومعالجة الفورم POST)"""
    if request.method == 'GET':
        # إذا تم فتح الرابط مباشرة، قم بعرض قالب صفحة تسجيل الدخول
        from flask import render_template
        return render_template('auth/login.html')

    try:
        # استقبال البيانات المتوافقة مع الحقول المرسلة من الفورم (username, password)
        username = str(request.form.get('username', '')).strip()
        password = str(request.form.get('password', ''))

        # التحقق من ملء الحقول الأساسية
        if not username or not password:
            return jsonify({
                'status': 'error', 
                'message': 'يرجى إدخال اسم المستخدم وكلمة المرور بشكل صحيح.'
            }), 400

        # البحث عن المشرف في قاعدة البيانات (تأكد من تعديل النماذج حسب مشروعك)
        # مثال افتراضي للبحث:
        # admin_staff = AdminStaff.query.filter(
        #     (AdminStaff.username == username) | (AdminStaff.email == username)
        # ).first()
        
        # --- (قالب تجريبي للتحقق - استبدله بمنطق قاعدة البيانات لديك) ---
        admin_staff = None # ضع استعلام قاعدة البيانات الحقيقي هنا

        if not admin_staff:
            logger.warning(f"⚠️ محاولة دخول فاشلة لمستخدِم غير موجود: {username}")
            return jsonify({
                'status': 'error', 
                'message': 'اسم المستخدم أو كلمة المرور غير صحيحة.'
            }), 401

        # تسجيل الدخول الناجح وتخزين الجلسة
        # login_user(admin_staff, remember=True)
        session['user_type'] = 'admin_staff'
        session['admin_logged_in'] = True
        session['login_time'] = datetime.now().isoformat()

        logger.info(f"🛡️ تم تسجيل دخول المشرف بنجاح: {username}")
        
        return jsonify({
            'status': 'success',
            'message': 'تم التحقق بنجاح. جاري التوجيه إلى النظام السيادي...',
            'redirect': url_for('auth_portal_bp.dashboard')
        })

    except Exception as e:
        logger.error(f"❌ خطأ فادح أثناء معالجة تسجيل الدخول للإدارة: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error', 
            'message': f'خطأ داخلي في الخادم: {str(e)}'
        }), 400
