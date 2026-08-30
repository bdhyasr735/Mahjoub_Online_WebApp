# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/seo_service.py

from flask import current_app

def get_seo_data(page_name='default', custom_seo=None):
    """دالة لتهيئة بيانات الـ SEO للصفحات وتجنب خطأ UndefinedError"""
    if custom_seo:
        return custom_seo
    
    seo_defaults = {
        'login': {
            'title': 'تسجيل دخول الموردين - محجوب أونلاين',
            'description': 'بوابة تسجيل الدخول الخاصة بموردي منصة محجوب أونلاين الرقمية.',
            'keywords': 'موردين, تسجيل دخول, محجوب أونلاين'
        },
        'register': {
            'title': 'انضم إلينا كمورد - محجوب أونلاين',
            'description': 'سجل الآن كمنشأة تجارية أو مورد وابدأ البيع معنا.',
            'keywords': 'تسجيل مورد جديد, انضم للمنصة'
        },
        'default': {
            'title': 'بوابة الموردين - محجوب أونلاين',
            'description': 'منصة متكاملة لإدارة المنتجات والطلبات والمحافظ المالية للموردين.',
            'keywords': 'محجوب أونلاين, لوحة المورد'
        }
    }
    
    return seo_defaults.get(page_name, seo_defaults['default'])
