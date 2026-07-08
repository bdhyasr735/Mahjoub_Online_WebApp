# apps/registry.py

# ... (الموديولات السابقة)

registered_modules = {
    # ... (الموديولات الأخرى الموجودة سابقاً)

    # إضافة موديول الصلاحيات
    'permissions': {
        'display_name': 'إدارة الصلاحيات',
        'icon': 'fas fa-shield-alt',
        'links': {
            'قائمة الأدوار': 'admin_permissions.roles_list',
            'إسناد الصلاحيات': 'admin_permissions.assign_permissions'
        }
    },

    # إضافة موديول العملات والصرف
    'exchange_management': {
        'display_name': 'الرقابة المالية والصرف',
        'icon': 'fas fa-money-bill-wave',
        'links': {
            'أسعار الصرف': 'admin_exchange.rates',
            'سجل العمليات': 'admin_exchange.transactions'
        }
    }
}
