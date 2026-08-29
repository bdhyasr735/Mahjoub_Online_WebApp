"""
apps/suppliers_auth_portal/registry.py
سجل موديول بوابة الموردين وموظفيهم والتعريفات الأساسية للأذونات والصلاحيات
"""

MODULE_INFO = {
    "name": "suppliers_auth_portal",
    "verbose_name": "بوابة الموردين وموظفيهم",
    "version": "2.5.0",
    "description": "منظومة تسجيل ودخول الموردين وموظفيهم مع إدارة المحفظة المالية الذكية وتحسين محركات البحث والظهور (SEO)",
    "author": "Royal Enterprise Solutions",
    "url_prefix": "/suppliers",
    "theme": {
        "primary_dark": "#05020a",
        "secondary_dark": "#0f071c",
        "accent_gold": "#ce9e49",
        "accent_gold_light": "#fae19c",
        "font_family": "Cairo, sans-serif",
    },
    "features": [
        "CSRF Protection via X-CSRFToken",
        "Dual-Factor OTP Password Recovery",
        "Automated Wallet & Virtual IBAN Generation",
        "Employee RBAC Permission Delegation",
        "Full Search Engine Optimization (SEO) & Schema.org JSON-LD",
        "Dynamic Sitemap.xml & Compliant Robots.txt",
    ],
}

# تعريفات الصلاحيات المعتمدة
class PERMISSIONS:
    SUPPLIER_OWNER = "supplier.owner"
    MANAGE_EMPLOYEES = "supplier.manage_employees"
    VIEW_WALLET = "supplier.view_wallet"
    WITHDRAW_WALLET = "supplier.withdraw_wallet"
    MANAGE_QUOTATIONS = "supplier.manage_quotations"
    VIEW_PURCHASE_ORDERS = "supplier.view_purchase_orders"
    DELIVERY_MANAGEMENT = "supplier.delivery_management"
    ACCOUNTING_VIEW = "supplier.accounting_view"

# أدوار موظفي الموردين المعتمدة مع الصلاحيات الافتراضية
EMPLOYEE_ROLES = {
    "manager": {
        "title_ar": "مدير العمليات والتوريد",
        "permissions": [
            PERMISSIONS.MANAGE_EMPLOYEES,
            PERMISSIONS.VIEW_WALLET,
            PERMISSIONS.MANAGE_QUOTATIONS,
            PERMISSIONS.VIEW_PURCHASE_ORDERS,
            PERMISSIONS.DELIVERY_MANAGEMENT,
        ],
    },
    "accountant": {
        "title_ar": "المحاسب المالي للمورد",
        "permissions": [
            PERMISSIONS.VIEW_WALLET,
            PERMISSIONS.ACCOUNTING_VIEW,
            PERMISSIONS.VIEW_PURCHASE_ORDERS,
        ],
    },
    "logistics": {
        "title_ar": "مسؤول الشحن والخدمات اللوجستية",
        "permissions": [
            PERMISSIONS.DELIVERY_MANAGEMENT,
            PERMISSIONS.VIEW_PURCHASE_ORDERS,
        ],
    },
    "sales": {
        "title_ar": "ممثل المبيعات والتعاقدات",
        "permissions": [
            PERMISSIONS.MANAGE_QUOTATIONS,
            PERMISSIONS.VIEW_PURCHASE_ORDERS,
        ],
    },
}

# إعدادات الأمان
SECURITY_CONFIG = {
    "csrf_header_primary": "X-CSRFToken",
    "csrf_header_secondary": "X-CSRF-Token",
    "otp_expiration_seconds": 300,  # 5 دقائق
    "otp_length": 6,
    "max_otp_attempts": 3,
    "min_password_length": 8,
}

# إعدادات تحسين محركات البحث والظهور (SEO Configuration)
SEO_CONFIG = {
    "site_name": "منظومة التوريد الملكية",
    "portal_name": "بوابة الموردين وموظفيهم",
    "default_keywords": [
        "بوابة الموردين",
        "تسجيل الموردين",
        "موظفو المورد",
        "المحفظة الرقمية",
        "السجل التجاري",
        "منافسات التوريد",
        "اعتماد الموردين",
        "المنظومة الملكية",
    ],
    "robots_directive": "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1",
    "sitemap_endpoint": "/suppliers/sitemap.xml",
    "robots_endpoint": "/suppliers/robots.txt",
    "schema_org_types": ["WebSite", "Organization", "WebApplication", "BreadcrumbList", "FAQPage"],
}
