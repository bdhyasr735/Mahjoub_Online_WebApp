# apps/supplier_wallet/context_processors.py

def inject_supplier_modules():
    """
    هذه الدالة تُستدعى في كل صفحة
    وتقوم بحقن المتغيرات في القوالب
    """
    supplier_modules = {}
    
    # 1. نحدد المورد الحالي
    supplier_id = get_current_supplier_id()
    
    # 2. نحدد معرف المحفظة
    w_id = get_wallet_id(supplier_id)
    
    # 3. نبني الروابط
    custom_links = {
        'supplier_wallet.transactions': 'حركة المحفظة',
        'supplier_wallet.withdraw': 'سحب الرصيد'
    }
    
    # 4. نبني هيكل الموديول
    module_payload = {
        'name': 'إدارة المالية',
        'title': 'إدارة المالية',
        'icon': 'fas fa-coins',
        'links': custom_links,
        'show_in_supplier': True
    }
    
    # 5. نضيفه إلى قاموس الموديولات
    supplier_modules['إدارة المالية'] = module_payload
    
    # 6. نرجعه ليتم استخدامه في القوالب
    return {'supplier_modules': supplier_modules}
