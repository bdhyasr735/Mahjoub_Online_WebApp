# apps/suppliers_dashboard/registry.py
"""
تسجيل موديولات وقوائم لوحة تحكم الموردين المركزية في منصة محجوب أونلاين.
تم تسجيل الموديولات يدوياً لتنظيم الروابط والصلاحيات بدقة.
"""

def get_supplier_modules():
    return {
        'dashboard': {
            'title': 'لوحة التحكم',
            'icon': 'fas fa-home',
            'links': {
                'suppliers_dashboard.dashboard_home': 'الرئيسية'
            }
        },
        'wallet': {
            'title': 'المحفظة والمالية',
            'icon': 'fas fa-wallet',
            'links': {
                'supplier_wallet.supplier_wallet_index': 'سجل المحفظة والحركات',
                'supplier_wallet.request_withdrawal': 'طلب سحب أرباح'
            }
        },
        'products': {
            'title': 'إدارة المنتجات',
            'icon': 'fas fa-boxes',
            'links': {
                'suppliers_dashboard.list_products': 'قائمة المنتجات',
                'suppliers_dashboard.add_product': 'إضافة منتج جديد'
            }
        },
        'staff': {
            'title': 'فريق العمل',
            'icon': 'fas fa-users-cog',
            'links': {
                'suppliers_dashboard.list_staff': 'إدارة الموظفين والصلاحيات'
            }
        },
        'settings': {
            'title': 'الإعدادات والملف',
            'icon': 'fas fa-user-cog',
            'links': {
                'suppliers_dashboard.profile_settings': 'إعدادات المتجر والملف'
            }
        }
    }
