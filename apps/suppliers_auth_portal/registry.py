"""
apps/suppliers_auth_portal/registry.py
سجل موديول بوابة الموردين وموظفيهم والتعريفات الأساسية للأذونات والصلاحيات
منصة اللامركزية لحوكمة التجارة اليمنية - محجوب أونلاين | سوقك الذكي
"""

MODULE_INFO = {
    "name": "suppliers_auth_portal",
    "verbose_name": "محجوب أونلاين - بوابة الموردين وموظفيهم",
    "version": "3.0.0",
    "description": "منصة اللامركزية لحوكمة التجارة اليمنية - بوابة الموردين وموظفيهم بسعر التكلفة وسعر الجملة مع المحفظة الرقمية الذكية، الحصن الرقمي AES-256، وتحسين محركات البحث والظهور (SEO)",
    "author": "محجوب أونلاين | منصة اللامركزية لحوكمة التجارة اليمنية",
    "url_prefix": "/suppliers",
    "theme": {
        "primary_dark": "#05020a",
        "secondary_dark": "#0f071c",
        "accent_gold": "#ce9e49",
        "accent_gold_light": "#fae19c",
        "font_family": "Cairo, sans-serif",
    },
    "features": [
        "Sovereign Digital Fortress with AES-256 Encryption",
        "Cost & Wholesale Pricing Governance Engine (Free Dashboard Charter)",
        "CSRF Protection via X-CSRFToken",
        "Dual-Factor OTP Password Recovery",
        "Automated Wallet & Virtual IBAN Generation",
        "Employee RBAC Permission Delegation",
        "Meta, TikTok & Microsoft Ecosystem Security Integrations",
        "Full Search Engine Optimization (SEO) & Schema.org JSON-LD",
        "Dynamic Sitemap.xml & Compliant Robots.txt",
    ],
}

# ميثاق حوكمة الأسعار المعتمد
PRICING_GOVERNANCE_CHARTER = {
    "policy_name": "ميثاق سعر التكلفة وسعر الجملة",
    "notice": "للعلم: التعامل بسعر التكلفة وسعر الجملة أو أسعار تقترب من الجملة وبأسعار تنافسية. في حالة رؤية الأسعار غير مناسبة سيتم توقيف لوحة التحكم مع العلم أنها مجاناً بالكامل.",
    "dashboard_fee": 0.0,
    "is_free_dashboard": True,
    "enforce_fair_pricing": True,
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
    SECURITY_FORTRESS_MANAGE = "supplier.security_fortress_manage"
    PRICING_GOVERNANCE_VIEW = "supplier.pricing_governance_view"


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
            PERMISSIONS.PRICING_GOVERNANCE_VIEW,
        ],
    },
    "accountant": {
        "title_ar": "المحاسب المالي للمورد",
        "permissions": [
            PERMISSIONS.VIEW_WALLET,
            PERMISSIONS.ACCOUNTING_VIEW,
            PERMISSIONS.VIEW_PURCHASE_ORDERS,
            PERMISSIONS.PRICING_GOVERNANCE_VIEW,
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
            PERMISSIONS.PRICING_GOVERNANCE_VIEW,
        ],
    },
    "security_officer": {
        "title_ar": "مسؤول الأمن والحصن الرقمي",
        "permissions": [
            PERMISSIONS.SECURITY_FORTRESS_MANAGE,
        ],
    },
}

# إعدادات الأمان والتشفير السيادي
SECURITY_CONFIG = {
    "encryption_algorithm": "AES-256-GCM",
    "key_derivation": "PBKDF2-SHA256",
    "csrf_header_primary": "X-CSRFToken",
    "csrf_header_secondary": "X-CSRF-Token",
    "otp_expiration_seconds": 300,  # 5 دقائق
    "otp_length": 6,
    "max_otp_attempts": 3,
    "min_password_length": 8,
    "integrations": ["Meta Conversion API / Pixel", "TikTok Events API", "Microsoft Clarity"],
}

# إعدادات تحسين محركات البحث والظهور (SEO Configuration)
SEO_CONFIG = {
    "site_name": "محجوب أونلاين - سوقك الذكي",
    "portal_name": "بوابة الموردين وموظفيهم - منصة اللامركزية لحوكمة التجارة اليمنية",
    "default_keywords": [
        "محجوب أونلاين",
        "سوقك الذكي",
        "منصة اللامركزية لحوكمة التجارة اليمنية",
        "بوابة الموردين",
        "تسجيل الموردين اليمن",
        "سعر التكلفة",
        "سعر الجملة",
        "المحفظة الرقمية الذكية",
        "لوحة تحكم الموردين مجانا",
        "الحصن الرقمي AES-256",
        "التجارة اليمنية الذكية",
    ],
    "robots_directive": "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1",
    "sitemap_endpoint": "/suppliers/sitemap.xml",
    "robots_endpoint": "/suppliers/robots.txt",
    "schema_org_types": ["WebSite", "Organization", "WebApplication", "BreadcrumbList", "FAQPage"],
}


