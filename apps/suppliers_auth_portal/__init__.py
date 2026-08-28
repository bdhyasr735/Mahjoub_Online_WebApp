"""
بوابة الموردين وموظفيهم (Suppliers & Employees Authentication Portal)
=====================================================================
موديول متكامل للمصادقة، التسجيل، إدارة المحافظ المالية، وموظفي الموردين
مع الالتزام بالهوية الملكية وحماية CSRF، وتحسين محركات البحث والظهور (SEO).
"""

from .routes import suppliers_bp
from .registry import MODULE_INFO, PERMISSIONS, SEO_CONFIG
from .auth_service import SupplierAuthService
from .seo_service import SEOService, seo_service, generate_sitemap_xml, generate_robots_txt

__version__ = "2.5.0"
__all__ = [
    "suppliers_bp",
    "MODULE_INFO",
    "PERMISSIONS",
    "SEO_CONFIG",
    "SupplierAuthService",
    "SEOService",
    "seo_service",
    "generate_sitemap_xml",
    "generate_robots_txt",
]
