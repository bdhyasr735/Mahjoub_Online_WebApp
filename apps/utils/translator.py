# 📂 apps/utils/translator.py

def translate_status(status_key):
    """
    تحويل حالات الطلب والدفع من الإنجليزية إلى العربية 
    بناءً على التسميات المعتمدة في النظام.
    """
    translations = {
        # حالات الطلب
        'pending': 'قيد الانتظار',
        'confirmed': 'مؤكد',
        'processing': 'تحت التجهيز',
        'shipped': 'تم الشحن',
        'delivered': 'تم التسليم',
        'cancelled': 'ملغي',
        'refunded': 'مسترد',
        
        # حالات الدفع
        'paid': 'مدفوع',
        'unpaid': 'غير مدفوع',
        'failed': 'فشل الدفع',
        
        # المصادر
        'store': 'المتجر',
        'funnel': 'فانل'
    }
    
    return translations.get(status_key.lower(), status_key)
