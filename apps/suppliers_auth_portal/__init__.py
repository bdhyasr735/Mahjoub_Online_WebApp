# apps/suppliers_auth_portal/__init__.py

"""
حزمة بوابة مصادقة الموردين (Suppliers Authentication Portal)
تتولى إدارة تسجيل الدخول، والتسجيل، واستعادة كلمة المرور للموردين وموظفيهم.
"""

from apps.suppliers_auth_portal.routes import suppliers_auth_bp, init_app

__all__ = ['suppliers_auth_bp', 'init_app']
