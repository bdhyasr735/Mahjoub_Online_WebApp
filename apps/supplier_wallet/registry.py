# registry.py - نظام تسجيل الموديولات والقوائم لمنصة محجوب أونلاين

class ModuleRegistry:
    def __init__(self):
        self.modules = {}

    def register(self, key, title, icon, links, order=10):
        """
        تسجيل موديول جديد داخل لوحة التحكم مع التحقق من صحة البيانات.
        """
        self.modules[key] = {
            'title': title,
            'icon': icon,
            'links': links,  # يجب أن يكون على شكل قواميس dict (endpoint: title)
            'order': order
        }

    def get_modules(self):
        """
        إرجاع الموديولات مرتبة تصاعدياً حسب الأولوية.
        """
        return dict(sorted(self.modules.items(), key=lambda item: item[1]['order']))

# إنشاء كائن التسجيل العام
registry = ModuleRegistry()

# ==========================================
# تسجيل الموديولات والروابط الأساسية للمنصة
# ==========================================

# 1. لوحة تحكم الموردين الرئيسية
registry.register(
    key='suppliers_dashboard',
    title='لوحة التحكم',
    icon='fas fa-tachometer-alt',
    links={
        'suppliers.dashboard': 'الرئيسية'
    },
    order=1
)

# 2. موديول الإدارة المالية والمحافظ للموردين
registry.register(
    key='supplier_wallet',
    title='الإدارة المالية',
    icon='fas fa-wallet',
    links={
        'supplier_wallet.wallet_dashboard': 'نظرة عامة على المحفظة',
        'supplier_wallet.transactions': 'سجل المعاملات المالية',
        'supplier_wallet.payouts': 'طلبات السحب والأرباح'
    },
    order=2
)

# 3. موديول إدارة المنتجات والطلبات
registry.register(
    key='supplier_operations',
    title='إدارة العمليات والطلبات',
    icon='fas fa-boxes',
    links={
        'supplier_operations.orders_list': 'طلبات العملاء',
        'supplier_operations.products_manage': 'إدارة المنتجات'
    },
    order=3
)

# 4. موديول إعدادات الحساب والموظفين
registry.register(
    key='supplier_settings',
    title='إعدادات الحساب',
    icon='fas fa-cogs',
    links={
        'suppliers.profile': 'الملف التجاري',
        'suppliers.staff_management': 'إدارة الموظفين والصلاحيات'
    },
    order=4
)
