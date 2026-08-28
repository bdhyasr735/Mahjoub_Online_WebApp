"""
apps/suppliers_auth_portal/seo_service.py
خدمة تحسين محركات البحث (SEO)، إدارة الوسوم الوصفية (Metadata)، وتوليد خريطة الموقع (Sitemap) وملف Robots.txt
"""

from typing import Dict, Any, List

class SeoService:
    """خدمة مركزية لإدارة بيانات التحسين لمحركات البحث الخاصة ببوابة الموردين"""

    def __init__(self):
        self.base_url = "https://mahjoob-online.com/suppliers"
        self.pages_meta = {
            "login": {
                "title": "تسجيل دخول الموردين والموظفين | محجوب أونلاين",
                "description": "بوابة تسجيل الدخول الآمنة للموردين والموظفين في منصة محجوب أونلاين لإدارة التوريدات، المبيعات، والمحافظ المالية.",
                "keywords": "تسجيل دخول موردين, محجوب أونلاين, لوحة تحكم الموردين, توريدات رقمية",
                "robots": "index, follow",
                "og_type": "website",
            },
            "register": {
                "title": "انضم إلينا كمورد معتمد | محجوب أونلاين",
                "description": "سجل الآن كمورد معتمد في منصة محجوب أونلاين، ووسع نطاق أعمالك التجارية مع تفعيل المحفظة المالية الرقمية الفورية.",
                "keywords": "تسجيل مورد جديد, انضم كمورد, محجوب أونلاين, توريد منتجات, التجارة الإلكترونية",
                "robots": "index, follow",
                "og_type": "website",
            },
            "forgot_password": {
                "title": "استعادة كلمة المرور | بوابة الموردين محجوب أونلاين",
                "description": "استعد الوصول إلى حسابك المعتمد أو حسابات الموظفين التابعين لك عبر التحقق الثنائي بخطوات آمنة وسريعة.",
                "keywords": "استعادة كلمة المرور, إعادة تعيين كلمة المرور, دعم الموردين, محجوب أونلاين",
                "robots": "noindex, follow",
                "og_type": "website",
            },
            "verify": {
                "title": "التحقق الأمني الثنائي (OTP) | محجوب أونلاين",
                "description": "أدخل رمز التحقق الأمني المرسل لتأكيد الحساب وإتمام عمليات المصادقة المتقدمة في منصة محجوب أونلاين.",
                "keywords": "تحقق OTP, أمان الحساب, تفعيل الموردين, محجوب أونلاين",
                "robots": "noindex, nofollow",
                "og_type": "website",
            }
        }

    def get_page_metadata(self, page_key: str) -> Dict[str, Any]:
        """إرجاع البيانات الوصفية الكاملة مع هيكلة Schema.org JSON-LD للصفحة المحددة"""
        meta = self.pages_meta.get(page_key, self.pages_meta["login"])
        
        # توليد هيكل البيانات المنظمة (Schema.org)
        schema_org = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": meta["title"],
            "description": meta["description"],
            "url": f"{self.base_url}/{page_key if page_key != 'login' else ''}",
            "publisher": {
                "@type": "Organization",
                "name": "محجوب أونلاين",
                "url": "https://mahjoob-online.com"
            }
        }

        return {
            "title": meta["title"],
            "description": meta["description"],
            "keywords": meta["keywords"],
            "robots": meta["robots"],
            "og_type": meta["og_type"],
            "canonical_url": f"{self.base_url}/{page_key if page_key != 'login' else ''}",
            "schema_org": schema_org
        }


def generate_robots_txt() -> str:
    """توليد محتوى ملف robots.txt مع حماية المسارات الحساسة وتوجيه عناكب البحث"""
    return """# Robots.txt for محجوب أونلاين - Suppliers Portal
User-agent: *
Allow: /suppliers/login
Allow: /suppliers/register
Allow: /suppliers/forgot-password
Disallow: /suppliers/verify
Disallow: /suppliers/dashboard
Disallow: /suppliers/wallet/
Disallow: /suppliers/employees

Sitemap: https://mahjoob-online.com/suppliers/sitemap.xml
"""


def generate_sitemap_xml() -> str:
    """توليد خريطة الموقع (Sitemap.xml) الديناميكية لصفحات الموديول العامة"""
    urls = [
        {"loc": "https://mahjoob-online.com/suppliers/login", "changefreq": "monthly", "priority": "1.0"},
        {"loc": "https://mahjoob-online.com/suppliers/register", "changefreq": "monthly", "priority": "0.9"},
        {"loc": "https://mahjoob-online.com/suppliers/forgot-password", "changefreq": "yearly", "priority": "0.3"}
    ]

    xml_items = []
    for u in urls:
        xml_items.append(f"""  <url>
    <loc>{u['loc']}</loc>
    <changefreq>{u['changefreq']}</changefreq>
    <priority>{u['priority']}</priority>
  </url>""")

    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{'\n'.join(xml_items)}
</urlset>"""

    return sitemap_content.strip()


# نسخة عامة للاستخدام البرمجي في المسارات والموديولات
seo_service = SeoService()
