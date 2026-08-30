# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/seo_service.py

def get_seo_data(page_name='default', custom_seo=None):
    """دالة لتهيئة بيانات الـ SEO ومحرك البحث وقوالب المشاركة الاجتماعية"""
    
    base_defaults = {
        'site_name': 'محجوب أونلاين',
        'og': {
            'site_name': 'محجوب أونلاين',
            'locale': 'ar_AR',
            'type': 'website',
            'title': 'بوابة الموردين - محجوب أونلاين',
            'description': 'منصة متكاملة لإدارة المنتجات والطلبات والمحافظ المالية للموردين.',
            'url': 'https://mahjoub.online/suppliers',
            'image': 'https://mahjoub.online/static/images/logo.webp'
        },
        'twitter': {
            'card': 'summary_large_image',
            'title': 'بوابة الموردين - محجوب أونلاين',
            'description': 'منصة متكاملة لإدارة المنتجات والطلبات والمحافظ المالية للموردين.',
            'image': 'https://mahjoub.online/static/images/logo.webp'
        },
        'jsonld': {
            '@context': 'https://schema.org',
            '@type': 'WebSite',
            'name': 'محجوب أونلاين',
            'url': 'https://mahjoub.online'
        },
        'noindex': False,
        'canonical_url': 'https://mahjoub.online/suppliers/login'
    }

    pages = {
        'login': {
            'title': 'تسجيل دخول الموردين - محجوب أونلاين',
            'description': 'بوابة تسجيل الدخول الخاصة بموردي منصة محجوب أونلاين الرقمية.',
            'keywords': 'موردين, تسجيل دخول, محجوب أونلاين',
            'canonical_url': 'https://mahjoub.online/suppliers/login'
        },
        'register': {
            'title': 'انضم إلينا كمورد - محجوب أونلاين',
            'description': 'سجل الآن كمنشأة تجارية أو مورد وابدأ البيع معنا بسعر التكلفة.',
            'keywords': 'تسجيل مورد جديد, انضم للمنصة, حوكمة الأسعار',
            'canonical_url': 'https://mahjoub.online/suppliers/register'
        },
        'forgot_password': {
            'title': 'استعادة كلمة المرور - محجوب أونلاين',
            'description': 'استعد بيانات الدخول الخاصة بحسابك في بوابة الموردين والموظفين.',
            'keywords': 'استعادة كلمة المرور, نسيت كلمة المرور',
            'canonical_url': 'https://mahjoub.online/suppliers/forgot-password'
        }
    }

    selected_page = pages.get(page_name, pages['login'])
    
    # دمج الخصائص الأساسية مع تفاصيل الصفحة المحددة
    merged_data = base_defaults.copy()
    merged_data.update(selected_page)
    merged_data['og'] = base_defaults['og'].copy()
    merged_data['og'].update({
        'title': selected_page['title'],
        'description': selected_page['description'],
        'url': selected_page['canonical_url']
    })
    merged_data['twitter'] = base_defaults['twitter'].copy()
    merged_data['twitter'].update({
        'title': selected_page['title'],
        'description': selected_page['description']
    })

    if custom_seo and isinstance(custom_seo, dict):
        merged_data.update(custom_seo)

    return merged_data
