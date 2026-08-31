from flask import Blueprint, request, jsonify, url_for, session
from datetime import datetime
import logging

# إعداد السجل (Logger) الخاص بالبوابة الإدارية السيادية
logger = logging.getLogger(__name__)

auth_portal_bp = Blueprint('auth_portal_bp', __name__, template_folder='templates')

@auth_portal_bp.route('/login', methods=['POST'])
def login():
    """معالجة تسجيل الدخول للمشرفين باستخدام بيانات الفورم التقليدية (Form Data)"""
    try:
        # استقبال البيانات مباشرة من request.form المتوافقة مع FormData في الجافاسكريبت
        login_input = str(request.form.get('username', '')).strip()
        password = str(request.form.get('password', ''))

        if not login_input or not password:
            return jsonify({'status': 'error', 'message': 'يرجى إدخال اسم المستخدم/البريد وكلمة المرور'}), 400

        # التحقق من المدخلات (مفترض وجود دالة validate_input مسبقاً في مشروعك)
        valid_input = validate_input(login_input)
        if not valid_input:
            return jsonify({'status': 'error', 'message': 'صيغة البيانات المدخلة غير مطابقة للمعايير'}), 400

        # البحث عن المشرف في قاعدة البيانات
        admin_staff = AdminStaff.query.filter(
            (AdminStaff.username == valid_input) | (AdminStaff.email == valid_input)
        ).first()

        if not admin_staff or not admin_staff.check_password(password):
            logger.warning(f"⚠️ محاولة دخول فاشلة (اسم مستخدم غير موجود أو كلمة مرور خاطئة): {login_input}")
            return jsonify({'status': 'error', 'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'}), 401

        if hasattr(admin_staff, 'is_active') and not admin_staff.is_active:
            logger.warning(f"⚠️ محاولة دخول على حساب إداري معطل: {valid_input}")
            return jsonify({'status': 'error', 'message': 'هذا الحساب الإداري معطل. يرجى مراجعة الإدارة العليا.'}), 403

        # تسجيل الدخول عبر مكتبة Flask-Login
        login_user(admin_staff, remember=True)
        session['user_type'] = 'admin_staff'
        session['login_time'] = datetime.now().isoformat()

        logger.info(f"🛡️ تم تسجيل دخول المشرف/الموظف بنجاح: {admin_staff.username}")
        
        return jsonify({
            'status': 'success',
            'message': 'تم التحقق بنجاح. جاري التوجيه إلى النظام السيادي...',
            'redirect': url_for('auth_portal_bp.dashboard')
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ فادح أثناء معالجة تسجيل الدخول: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'خطأ داخلي في الخادم: {str(e)}'}), 500
