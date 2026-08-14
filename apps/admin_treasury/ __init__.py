"""
apps/admin_treasury/__init__.py
حزمة موديول الخزينة المركزية وحسابات الضمان
مشروع Mahjoub Online WebApp
"""

from flask import Blueprint

def create_admin_treasury_blueprint():
    """
    إنشاء وتهيئة مخطط الخزينة المركزية (Admin Treasury Blueprint)
    """
    treasury_bp = Blueprint(
        'admin_treasury',
        __name__,
        url_prefix='/admin/treasury',
        template_folder='templates'
    )

    from .routes import treasury_controller
    treasury_bp.register_blueprint(treasury_controller.bp)

    return treasury_bp
