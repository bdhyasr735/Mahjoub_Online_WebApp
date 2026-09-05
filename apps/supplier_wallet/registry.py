def get_sidebar_modules():
    """دالة مساعدة لجلب الموديولات والقوائم الجانبية الخاصة بلوحة تحكم المورد"""
    supplier_modules = {}
    
    # محاولة جلب الموديولات من السجل الرئيسي
    try:
        from apps.suppliers_dashboard.registry import MODULES_REGISTRY
        if MODULES_REGISTRY:
            supplier_modules = MODULES_REGISTRY.copy()
    except ImportError:
        pass
    
    # محاولة جلب الموديولات من current_app
    if not supplier_modules and hasattr(current_app, 'supplier_modules') and current_app.supplier_modules:
        supplier_modules = current_app.supplier_modules.copy()
    
    # ✅ القائمة الاحتياطية الكاملة (جميع الموديولات)
    if not supplier_modules:
        supplier_modules = {
            'suppliers_dashboard': {
                'title': 'الرئيسية',
                'icon': 'fas fa-chart-pie',
                'links': {
                    'suppliers_dashboard.index': 'الرئيسية'
                }
            },
            'supplier_products': {
                'title': 'إدارة المنتجات',
                'icon': 'fas fa-box',
                'links': {
                    'supplier_products.index': 'جميع المنتجات',
                    'supplier_products.add': 'إضافة منتج جديد'
                }
            },
            'supplier_orders': {
                'title': 'المبيعات والطلبات',
                'icon': 'fas fa-shopping-cart',
                'links': {
                    'supplier_orders.index': 'الطلبات الواردة',
                    'supplier_orders.history': 'سجل المبيعات'
                }
            },
            'supplier_wallet': {
                'title': 'الإدارة المالية',
                'icon': 'fas fa-coins',
                'links': {
                    'supplier_wallet.transactions_redirect': 'حركة المحفظة',
                    'supplier_wallet.withdraw_redirect': 'سحب الرصيد'
                }
            },
            'supplier_staff': {
                'title': 'الموظفين',
                'icon': 'fas fa-users',
                'links': {
                    'supplier_staff.index': 'قائمة الموظفين',
                    'supplier_staff.add': 'إضافة موظف'
                }
            }
        }
    
    return supplier_modules
