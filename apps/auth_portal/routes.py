from flask import Blueprint, request, jsonify, url_for, session, render_template
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

auth_portal_bp = Blueprint('auth_portal_bp', __name__, template_folder='templates')

@auth_portal_bp.route('/login', methods=['GET', 'POST'])
def login():
    """معالجة تسجيل دخول المشرفين للبوابة السيادية بناءً على بيانات النظام"""
    if request.method == 'GET':
        return render_template('auth/login.html')

    try:
        # استقبال البيانات المرسلة عبر FormData من الواجهة الأمامية
        username = str(request.form.get('username', '')).strip()
        password = str(request.form.get('password', ''))

        # التحقق من ملء الحقول الإجبارية
        if not username or not password:
            return jsonify({
                'status': 'error', 
                'message': 'يرجى إدخال اسم المستخدم وكلمة المرور بدقة.'
            }), 400

        # الاستعلام الفعلي عن المشرف أو الموظف الإداري في قاعدة البيانات
        admin_staff = AdminStaff.query.filter(
            (AdminStaff.username == username) | (AdminStaff.email == username)
        ).first()

        # التحقق من صحة كلمة المرور ووجود الحساب
        if not admin_staff or not admin_staff.check_password(password):
            logger.warning(f"⚠️ محاولة دخول إداري فاشلة لاسم المستخدم: {username}")
            return jsonify({
                'status': 'error', 
                'message': 'اسم المستخدم أو كلمة المرور غير صحيحة.'
            }), 401

        # التحقق من حالة تفعيل الحساب الإداري
        if hasattr(admin_staff, 'is_active') and not admin_staff.is_active:
            logger.warning(f"⚠️ محاولة دخول على حساب إداري معطل: {username}")
            return jsonify({
                'status': 'error', 
                'message': 'هذا الحساب الإداري معطل. يرجى مراجعة الصلاحيات العليا.'
            }), 403

        # اعتماد تسجيل الدخول عبر نظام المصادقة وتوثيق الجلسة
        login_user(admin_staff, remember=True)
        session['user_type'] = 'admin_staff'
        session['login_time'] = datetime.now().isoformat()

        logger.info(f"🛡️ تم تسجيل دخول المشرف السيادي بنجاح: {admin_staff.username}")
        
        return jsonify({
            'status': 'success',
            'message': 'تم التحقق بنجاح. جاري التوجيه إلى لوحة التحكم السيادية...',
            'redirect': url_for('auth_portal_bp.dashboard')
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ فادح أثناء معالجة تسجيل دخول المشرفين: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error', 
            'message': f'خطأ داخلي في الخادم: {str(e)}'
        }), 500
