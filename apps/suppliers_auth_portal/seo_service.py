# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/seo_service.py
# خدمة تحسين محركات البحث (SEO) - تدعم جميع صفحات بوابة الموردين

from flask import request, url_for, current_app
from datetime import datetime


class SupplierPortalSEOService:
    """
    خدمة SEO المتكاملة لبوابة الموردين
    توفر البيانات الوصفية لجميع الصفحات مع دعم Open Graph و Twitter Cards و JSON-LD
    """
    
    # الإعدادات الأساسية للموقع
    SITE_NAME = "محجوب أونلاين - سوقك الذكي"
    SITE_URL = "https://mahjoub.online"
    SITE_LOGO = "https://cdn.qumra.cloud/media/67f7f6d5f0b82f44a47bf845/1770229315912-117966978.webp"
    SITE_DESCRIPTION = "منصة اللامركزية لحوكمة التجارة اليمنية - بوابة الموردين وموظفيهم المعتمدة"
    AUTHOR = "منصة اللامركزية لحوكمة التجارة اليمنية"
    
    @staticmethod
    def get_meta_tags(page_name, custom_data=None):
        """
        الحصول على البيانات الوصفية للصفحة
        
        Args:
            page_name (str): اسم الصفحة (login, register, verify, forgot_password, reset_password)
            custom_data (dict): بيانات مخصصة لتجاوز القيم الافتراضية
        
        Returns:
            dict: قاموس يحتوي على جميع البيانات الوصفية
        """
        
        # البيانات الأساسية
        base_seo = {
            "site_name": SupplierPortalSEOService.SITE_NAME,
            "author": SupplierPortalSEOService.AUTHOR,
            "site_url": SupplierPortalSEOService.SITE_URL,
            "logo": SupplierPortalSEOService.SITE_LOGO,
            "default_image": SupplierPortalSEOService.SITE_LOGO,
            "locale": "ar_AR",
            "robots": "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
        }
        
        # البيانات الخاصة بكل صفحة
        pages = {
            "login": {
                "title": "تسجيل دخول الموردين وموظفيهم | البوابة الملكية",
                "description": "بوابة الدخول المعتمدة للموردين وموظفيهم في منصة محجوب أونلاين. تداول بسعر التكلفة وبأسعار تنافسية تحت ميثاق حوكمة التجارة.",
                "keywords": "تسجيل دخول, بوابة الموردين, محجوب أونلاين, حوكمة التجارة, سعر التكلفة",
                "og_type": "website",
                "twitter_card": "summary_large_image",
                "priority": 1.0,
                "changefreq": "weekly"
            },
            "register": {
                "title": "اشتراك مورد جديد وإنشاء المحفظة المالية | المنظومة الملكية",
                "description": "سجل منشأتك الآن كمورد معتمد في محجوب أونلاين. احصل على لوحة تحكم مجانية بالكامل ومحفظة رقمية ذكية لتسوية مستحقات التوريد فوراً.",
                "keywords": "اشتراك مورد, تسجيل مورد, محفظة رقمية, لوحة تحكم مجانية, توريد اليمن",
                "og_type": "website",
                "twitter_card": "summary_large_image",
                "priority": 0.9,
                "changefreq": "monthly"
            },
            "verify": {
                "title": "التحقق من الحساب والمصادقة | محجوب أونلاين",
                "description": "أدخل رمز التحقق (OTP) لإتمام المصادقة وتفعيل لوحة التحكم والمحفظة الرقمية الخاصة بالمنشأة.",
                "keywords": "التحقق من الحساب, OTP, تفعيل الحساب, مصادقة ثنائية, محجوب أونلاين",
                "og_type": "website",
                "twitter_card": "summary",
                "priority": 0.7,
                "changefreq": "never"
            },
            "forgot_password": {
                "title": "استعادة كلمة المرور | البوابة الملكية للموردين",
                "description": "استعد بيانات حسابك أو كلمة مرور منشأتك بأمان تام عبر رمز التحقق المعتمد (OTP) في منصة محجوب أونلاين.",
                "keywords": "استعادة كلمة المرور, نسيت كلمة المرور, OTP, حماية الحساب, محجوب أونلاين",
                "og_type": "website",
                "twitter_card": "summary",
                "priority": 0.6,
                "changefreq": "never"
            },
            "reset_password": {
                "title": "إعادة تعيين كلمة المرور | البوابة الملكية",
                "description": "قم بإنشاء كلمة مرور جديدة وآمنة لحسابك لاستعادة الصلاحيات الكاملة في لوحة تحكم محجوب أونلاين.",
                "keywords": "إعادة تعيين كلمة المرور, كلمة مرور جديدة, أمان الحساب, محجوب أونلاين",
                "og_type": "website",
                "twitter_card": "summary",
                "priority": 0.6,
                "changefreq": "never"
            },
            "dashboard": {
                "title": "لوحة تحكم الموردين | محجوب أونلاين",
                "description": "لوحة التحكم الملكية للموردين وموظفيهم. إدارة الطلبات، المنتجات، المحفظة الرقمية، والإحصائيات لحوكمة التجارة اليمنية.",
                "keywords": "لوحة تحكم, موردين, محفظة رقمية, إدارة الطلبات, حوكمة التجارة",
                "og_type": "website",
                "twitter_card": "summary_large_image",
                "priority": 0.8,
                "changefreq": "daily",
                "noindex": True
            },
            "profile": {
                "title": "الملف الشخصي | محجوب أونلاين",
                "description": "إدارة الملف الشخصي للمورد وموظفيه في منصة محجوب أونلاين.",
                "keywords": "ملف شخصي, إدارة الحساب, مورد, محجوب أونلاين",
                "og_type": "website",
                "twitter_card": "summary",
                "priority": 0.5,
                "changefreq": "monthly",
                "noindex": True
            }
        }
        
        # الحصول على بيانات الصفحة المطلوبة
        page_data = pages.get(page_name, pages["login"]).copy()
        
        # دمج البيانات المخصصة
        if custom_data:
            page_data.update(custom_data)
        
        # إنشاء البيانات الكاملة للـ SEO
        full_data = {
            **base_seo,
            **page_data,
            "title": page_data.get("title", base_seo["site_name"]),
            "description": page_data.get("description", base_seo["SITE_DESCRIPTION"]),
            "keywords": page_data.get("keywords", ""),
            "canonical_url": SupplierPortalSEOService._get_canonical_url(page_name),
            "og": {
                "title": page_data.get("title", base_seo["site_name"]),
                "description": page_data.get("description", base_seo["SITE_DESCRIPTION"]),
                "url": SupplierPortalSEOService._get_canonical_url(page_name),
                "image": page_data.get("image", base_seo["default_image"]),
                "type": page_data.get("og_type", "website"),
                "site_name": base_seo["site_name"],
                "locale": base_seo["locale"]
            },
            "twitter": {
                "card": page_data.get("twitter_card", "summary_large_image"),
                "title": page_data.get("title", base_seo["site_name"]),
                "description": page_data.get("description", base_seo["SITE_DESCRIPTION"]),
                "image": page_data.get("image", base_seo["default_image"])
            },
            "jsonld": SupplierPortalSEOService._get_jsonld(page_name, page_data),
            "sitemap": {
                "priority": page_data.get("priority", 0.5),
                "changefreq": page_data.get("changefreq", "monthly")
            },
            "noindex": page_data.get("noindex", False)
        }
        
        return full_data
    
    @staticmethod
    def _get_canonical_url(page_name):
        """الحصول على الرابط الأساسي للصفحة"""
        try:
            endpoints = {
                "login": "suppliers_auth.login",
                "register": "suppliers_auth.register",
                "verify": "suppliers_auth.verify",
                "forgot_password": "suppliers_auth.forgot_password",
                "reset_password": "suppliers_auth.reset_password",
                "dashboard": "suppliers_dashboard.dashboard",
                "profile": "suppliers_auth.profile"
            }
            
            endpoint = endpoints.get(page_name)
            if endpoint:
                return url_for(endpoint, _external=True)
            
            return request.url
            
        except Exception:
            return request.url
    
    @staticmethod
    def _get_jsonld(page_name, page_data):
        """إنشاء بيانات JSON-LD للتكامل مع محركات البحث"""
        base_jsonld = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": page_data.get("title", SupplierPortalSEOService.SITE_NAME),
            "description": page_data.get("description", SupplierPortalSEOService.SITE_DESCRIPTION),
            "url": SupplierPortalSEOService._get_canonical_url(page_name),
            "inLanguage": "ar",
            "isPartOf": {
                "@type": "WebSite",
                "name": SupplierPortalSEOService.SITE_NAME,
                "url": SupplierPortalSEOService.SITE_URL
            }
        }
        
        # إضافة بيانات إضافية حسب نوع الصفحة
        if page_name == "login":
            base_jsonld["@type"] = "LoginPage"
            base_jsonld["potentialAction"] = {
                "@type": "AuthenticateAction",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": SupplierPortalSEOService._get_canonical_url("login")
                }
            }
            
        elif page_name == "register":
            base_jsonld["@type"] = "RegistrationPage"
            base_jsonld["potentialAction"] = {
                "@type": "RegisterAction",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": SupplierPortalSEOService._get_canonical_url("register")
                }
            }
            
        elif page_name in ["forgot_password", "reset_password"]:
            base_jsonld["@type"] = "PasswordRecoveryPage"
            base_jsonld["potentialAction"] = {
                "@type": "ResetPasswordAction",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": SupplierPortalSEOService._get_canonical_url(page_name)
                }
            }
        
        return base_jsonld


# ============================================================
# دوال مساعدة للاستخدام السهل في القوالب
# ============================================================

def get_seo_data(page_name, custom_data=None):
    """دالة مساعدة للحصول على بيانات SEO للقوالب"""
    return SupplierPortalSEOService.get_meta_tags(page_name, custom_data)


def get_page_title(page_name, custom_title=None):
    """دالة مساعدة للحصول على عنوان الصفحة للقوالب"""
    if custom_title:
        return f"{custom_title} | {SupplierPortalSEOService.SITE_NAME}"
    data = SupplierPortalSEOService.get_meta_tags(page_name)
    return data.get("title", SupplierPortalSEOService.SITE_NAME)


def get_page_description(page_name, custom_description=None):
    """دالة مساعدة للحصول على وصف الصفحة للقوالب"""
    if custom_description:
        return custom_description
    data = SupplierPortalSEOService.get_meta_tags(page_name)
    return data.get("description", SupplierPortalSEOService.SITE_DESCRIPTION)


# ============================================================
# تصدير الفئة والدوال الرئيسية
# ============================================================

__all__ = [
    'SupplierPortalSEOService',
    'get_seo_data',
    'get_page_title',
    'get_page_description'
]
