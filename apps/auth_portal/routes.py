from flask import Blueprint, request, jsonify, url_for, session, render_template
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

auth_portal_bp = Blueprint('auth_portal_bp', __name__, template_folder='templates')

@auth_portal_bp.route('/login', methods=['GET', 'POST'])
def login():
    """بوابة تسجيل دخول المشرفين السيادية"""
    if request.method == 'GET':
        return render_template('auth/login.html')

    try:
        # استقبال البيانات الواردة من كائن FormData عبر JavaScript
        username = str(request.form.get('username', '')).strip()
        password = str(request.form.get('password', ''))

        # التحقق من إدخال الحقول الأساسية
        if not username or not password:
            return jsonify({
                'status': 'error', 
                'message': 'يرجى إدخال اسم المستخدم وكلمة المرور.'
            }), 400

        # استعلام التحقق من المشرف في قاعدة البيانات
        # admin_staff = AdminStaff.query.filter(
        #     (AdminStaff.username == username) | (AdminStaff.email == username)
        # ).first()
        
        # نموذج افتراضي (استبدله بمنطق قاعدة البيانات لديك)
        admin_staff = None 

        if not admin_staff:
            logger.warning(f"⚠️ محاولة دخول فاشلة لمستخدِم غير موجود: {username}")
            return jsonify({
                'status': 'error', 
                'message': 'اسم المستخدم أو كلمة المرور غير صحيحة.'
            }, 401) # تم تعديل رمز الحالة ليكون 401 للخطأ في بيانات الاعتماد بدلاً من 400

        # تخزين بيانات الجلسة عند النجاح
        session['user_type'] = 'admin_staff'
        session['admin_logged_in'] = True
        session['login_time'] = datetime.now().isoformat()

        logger.info(f"🛡️ تم تسجيل دخول المشرف بنجاح: {username}")
        
        return jsonify({
            'status': 'success',
            'message': 'تم التحقق بنجاح. جاري التوجيه إلى النظام السيادي...',
            'redirect': url_for('auth_portal_bp.dashboard')
        }), 200

    except Exception as e:
        logger.error(f"❌ خطأ فادح أثناء معالجة تسجيل الدخول للإدارة: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error', 
            'message': f'خطأ داخلي في الخادم: {str(e)}'
        }), 500
