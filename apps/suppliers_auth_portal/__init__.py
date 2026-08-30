# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/__init__.py
# بوابة المصادقة للموردين وموظفيهم - تهيئة البلوبرنت وتجميع المحركات

from flask import Blueprint, render_template, current_app, g, request, session, redirect, url_for, flash
from flask_login import current_user
import os
from datetime import datetime

from apps.extensions import db, mail, csrf


# ============================================================
# إنشاء البلوبرنت الرئيسي
# ============================================================

bp = Blueprint(
    'suppliers_auth_portal',
    __name__,
    template_folder='templates/suppliers_auth_portal',
    static_folder='static',
    static_url_path='/supplier/static',
    url_prefix='/supplier'
)


# ============================================================
# استيراد المحركات (يتم بعد إنشاء البلوبرنت لتجنب الـ circular imports)
# ============================================================

from . import auth_login, auth_register, auth_recovery, seo_service


# ============================================================
# تسجيل البلوبرنتات الفرعية
# ============================================================

# محرك تسجيل الدخول
bp.register_blueprint(auth_login.bp)

# محرك التسجيل
bp.register_blueprint(auth_register.bp)

# محرك استعادة كلمة المرور
bp.register_blueprint(auth_recovery.bp)

# خدمة SEO (سيتم تسجيلها في seo_service)


# ============================================================
# معالجات ما قبل الطلب (Before Request)
# ============================================================

@bp.before_app_request
def load_supplier_portal_config():
    """
    تحميل إعدادات بوابة الموردين قبل كل طلب
    """
    if not hasattr(g, 'supplier_portal_loaded'):
        # إعدادات البوابة
        g.supplier_portal_loaded = True
        g.supplier_portal_name = 'بوابة الموردين وموظفيهم'
        g.supplier_portal_version = '1.0.0'
        
        # وقت التحميل
        g.load_time = datetime.utcnow()


@bp.before_request
def check_supplier_auth():
    """
    التحقق من صلاحيات الوصول للصفحات المحمية
    """
    # الصفحات العامة التي لا تحتاج إلى تسجيل دخول
    public_routes = [
        'auth_login.login',
        'auth_register.register_page',
        'auth_register.register',
        'auth_register.check_username',
        'auth_register.check_phone',
        'auth_register.check_email',
        'auth_recovery.forgot_password',
        'auth_recovery.request_otp',
        'auth_recovery.reset_password',
        'auth_recovery.resend_otp',
        'auth_recovery.verify'
    ]
    
    # الصفحات التي تحتاج إلى تسجيل دخول
    protected_routes = [
        'auth_login.logout',
        'auth_login.dashboard',
        'auth_login.profile'
    ]
    
    # الحصول على اسم النقطة الحالية
    endpoint = request.endpoint
    
    # إذا كان المستخدم غير مسجل الدخول ويحاول الوصول إلى صفحة محمية
    if not current_user.is_authenticated and endpoint and endpoint in protected_routes:
        flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'warning')
        return redirect(url_for('auth_login.login', next=request.url))
    
    # إذا كان المستخدم مسجل الدخول ويحاول الوصول إلى صفحة تسجيل الدخول
    if current_user.is_authenticated and endpoint and endpoint in ['auth_login.login', 'auth_register.register_page', 'auth_recovery.forgot_password']:
        return redirect(url_for('auth_login.dashboard'))


@bp.before_request
def set_supplier_context():
    """
    تعيين المتغيرات العامة للقوالب
    """
    g.supplier_user = current_user if current_user.is_authenticated else None
    g.supplier_is_authenticated = current_user.is_authenticated
    
    # تحديد نوع المستخدم
    if current_user.is_authenticated:
        from apps.models.supplier_db import Supplier
        from apps.models.supplier_staff_db import SupplierStaff
        
        if isinstance(current_user, Supplier):
            g.supplier_user_type = 'supplier'
        elif isinstance(current_user, SupplierStaff):
            g.supplier_user_type = 'employee'
        else:
            g.supplier_user_type = 'unknown'
    else:
        g.supplier_user_type = None


# ============================================================
# معالجات ما بعد الطلب (After Request)
# ============================================================

@bp.after_app_request
def add_security_headers(response):
    """
    إضافة رؤوس أمان إلى جميع استجابات البوابة
    """
    # منع تضمين الصفحة في iframe من مواقع أخرى
    response.headers['X-Frame-Options'] = 'DENY'
    
    # حماية من هجمات MIME-Sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # حماية من هجمات Cross-Site Scripting (XSS)
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # سياسة المصادر (CSP) الأساسية
    # يمكن توسيعها حسب الحاجة
    csp = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://fonts.googleapis.com https://cdn.qumra.cloud",
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com",
        "font-src 'self' https://fonts.gstatic.com https://cdn.qumra.cloud",
        "img-src 'self' data: https://cdn.qumra.cloud",
        "connect-src 'self' https://cdn.qumra.cloud"
    ]
    response.headers['Content-Security-Policy'] = '; '.join(csp)
    
    # منع المتصفح من تخمين نوع المحتوى
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    return response


# ============================================================
# معالج الأخطاء العام
# ============================================================

@bp.app_errorhandler(404)
def not_found_error(error):
    """صفحة خطأ 404 مخصصة"""
    if request.is_json:
        return {'success': False, 'message': 'الصفحة غير موجودة'}, 404
    
    return render_template('suppliers_auth_portal/errors/404.html'), 404


@bp.app_errorhandler(403)
def forbidden_error(error):
    """صفحة خطأ 403 مخصصة"""
    if request.is_json:
        return {'success': False, 'message': 'لا تملك صلاحية للوصول'}, 403
    
    flash('لا تملك صلاحية للوصول إلى هذه الصفحة', 'danger')
    return redirect(url_for('auth_login.dashboard'))


@bp.app_errorhandler(500)
def internal_error(error):
    """صفحة خطأ 500 مخصصة"""
    if request.is_json:
        return {'success': False, 'message': 'حدث خطأ داخلي في الخادم'}, 500
    
    flash('حدث خطأ داخلي في الخادم. يرجى المحاولة مرة أخرى.', 'danger')
    return redirect(url_for('auth_login.dashboard'))


# ============================================================
# دوال مساعدة للقوالب (Context Processors)
# ============================================================

@bp.app_context_processor
def utility_processor():
    """
    إضافة دوال مساعدة إلى جميع القوالب
    """
    def get_supplier_portal_name():
        return 'بوابة الموردين وموظفيهم'
    
    def get_current_year():
        return datetime.utcnow().year
    
    def get_supplier_version():
        return '1.0.0'
    
    def is_supplier_authenticated():
        return current_user.is_authenticated
    
    def get_supplier_user_type():
        if current_user.is_authenticated:
            from apps.models.supplier_db import Supplier
            from apps.models.supplier_staff_db import SupplierStaff
            
            if isinstance(current_user, Supplier):
                return 'supplier'
            elif isinstance(current_user, SupplierStaff):
                return 'employee'
        return None
    
    def mask_identifier(identifier):
        """إخفاء جزء من المعرف للعرض"""
        if not identifier:
            return identifier
        
        # إذا كان بريداً إلكترونياً
        if '@' in identifier:
            parts = identifier.split('@')
            if len(parts[0]) > 2:
                masked = parts[0][:2] + '***' + parts[0][-1:]
            else:
                masked = parts[0][:1] + '***'
            return f"{masked}@{parts[1]}"
        
        # إذا كان رقم هاتف
        digits = ''.join(filter(str.isdigit, identifier))
        if len(digits) >= 9:
            return f"{digits[:3]}****{digits[-2:]}"
        
        # إذا كان اسم مستخدم
        if len(identifier) > 3:
            return f"{identifier[:2]}***{identifier[-1:]}"
        
        return identifier
    
    def get_supplier_status_badge(status):
        """الحصول على شارة حالة الحساب"""
        badges = {
            'active': ('نشط', 'bg-emerald-500'),
            'inactive': ('غير نشط', 'bg-red-500'),
            'suspended': ('موقوف', 'bg-amber-500'),
            'pending': ('قيد الانتظار', 'bg-blue-500'),
            'blocked': ('محظور', 'bg-rose-700')
        }
        if status in badges:
            return badges[status]
        return ('غير معروف', 'bg-gray-500')
    
    return {
        'supplier_portal_name': get_supplier_portal_name,
        'current_year': get_current_year,
        'supplier_version': get_supplier_version,
        'is_supplier_authenticated': is_supplier_authenticated,
        'get_supplier_user_type': get_supplier_user_type,
        'mask_identifier': mask_identifier,
        'get_supplier_status_badge': get_supplier_status_badge
    }


# ============================================================
# تهيئة البلوبرنت عند تحميل التطبيق
# ============================================================

def init_app(app):
    """
    تهيئة بوابة الموردين مع التطبيق الرئيسي
    """
    # تسجيل البلوبرنت
    app.register_blueprint(bp)
    
    # إضافة تكوينات إضافية
    app.config.setdefault('SUPPLIER_PORTAL_NAME', 'بوابة الموردين وموظفيهم')
    app.config.setdefault('SUPPLIER_PORTAL_VERSION', '1.0.0')
    
    # تمكين CSRF لجميع نماذج البوابة
    csrf.init_app(app)
    
    # طباعة رسالة التأكيد في سجلات التطبيق
    app.logger.info('✅ تم تهيئة بوابة الموردين وموظفيهم بنجاح')
    
    return app


# ============================================================
# تصدير البلوبرنت والوظائف الرئيسية
# ============================================================

__all__ = [
    'bp',
    'init_app',
    'auth_login',
    'auth_register', 
    'auth_recovery',
    'seo_service'
]
