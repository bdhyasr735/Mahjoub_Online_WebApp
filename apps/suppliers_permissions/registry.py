# -*- coding: utf-8 -*-
# 📂 apps/supplier_permissions/registry.py

"""
سجل الصلاحيات المتاحة لموظفي الموردين والمساعدين في منصة محجوب أونلاين
mahjoub.online Supplier Permissions Registry
"""

SUPPLIER_PERMISSIONS_REGISTRY = {
    'orders': {
        'title': 'إدارة الطلبات والشحن',
        'icon': 'bi-box-seam',
        'color': '#4A154B',
        'items': {
            'view_orders': 'عرض وتصفح قائمة الطلبات',
            'process_orders': 'تغيير حالة الطلبات وإعداد الشحنات',
            'cancel_orders': 'إلغاء الطلبات ورفع الملاحظات',
            'export_orders': 'تصدير تقارير الطلبات'
        }
    },
    'products': {
        'title': 'إدارة المنتجات والمخزون',
        'icon': 'bi-bag',
        'color': '#4A154B',
        'items': {
            'view_products': 'عرض شجرة المنتجات والأسعار',
            'edit_products': 'تحديث الأسعار وإضافة كميات المخزون',
            'add_products': 'إضافة منتجات جديدة واقتراح الأصناف'
        }
    },
    'financials': {
        'title': 'المالية والمحفظة',
        'icon': 'bi-wallet2',
        'color': '#4A154B',
        'items': {
            'view_wallet': 'عرض رصيد المحفظة والحركات المالية',
            'request_payout': 'طلب سحب الأرباح والتحويل البنكي',
            'view_invoices': 'عرض واستخراج الفواتير الضريبية'
        }
    },
    'analytics': {
        'title': 'التقارير والإحصائيات',
        'icon': 'bi-graph-up-arrow',
        'color': '#4A154B',
        'items': {
            'view_analytics': 'متابعة مؤشرات الأداء وحجم المبيعات',
            'export_reports': 'تنزيل التقارير الإحصائية المتقدمة'
        }
    },
    'staff': {
        'title': 'إدارة الموظفين والصلاحيات',
        'icon': 'bi-people',
        'color': '#4A154B',
        'items': {
            'manage_staff': 'إضافة وتعديل بيانات الموظفين والمساعدين',
            'assign_permissions': 'تخصيص وتحديث جدول الصلاحيات'
        }
    }
}

DEFAULT_WORKER_PERMISSIONS = {
    'orders': ['view_orders', 'process_orders'],
    'products': ['view_products', 'edit_products'],
    'financials': [],
    'analytics': ['view_analytics'],
    'staff': []
}

DEFAULT_MANAGER_PERMISSIONS = {
    'orders': ['view_orders', 'process_orders', 'cancel_orders', 'export_orders'],
    'products': ['view_products', 'edit_products', 'add_products'],
    'financials': ['view_wallet', 'view_invoices'],
    'analytics': ['view_analytics', 'export_reports'],
    'staff': ['manage_staff']
}
