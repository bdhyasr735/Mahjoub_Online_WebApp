import uuid
import random
import string

def generate_wallet_id(prefix="W-MAH-"):
    """
    توليد رقم محفظة سيادي فريد لمنصة محجوب أونلاين.
    مثال الناتج: W-MAH-9631
    """
    # توليد 4 أرقام عشوائية لضمان التميز في الترسانة الرقمية
    random_digits = ''.join(random.choices(string.digits, k=4))
    
    # دمج البادئة مع الأرقام لتشكيل الهوية المالية
    wallet_id = f"{prefix}{random_digits}"
    
    return wallet_id

def validate_wallet_balance(vendor):
    """
    التحقق من جاهزية أرصدة المورد قبل أي عملية تعميد مالي لضمان استقرار النظام.
    """
    balances = {
        'YER': getattr(vendor, 'balance_yer', 0.0) or 0.0,
        'SAR': getattr(vendor, 'balance_sar', 0.0) or 0.0,
        'USD': getattr(vendor, 'balance_usd', 0.0) or 0.0
    }
    return balances

def format_currency(amount, currency="YER"):
    """
    تنسيق المبالغ المالية لتظهر بشكل لائق في واجهات محجوب أونلاين.
    """
    if currency == "YER":
        return f"{amount:,.0f} ريال يمني"
    elif currency == "SAR":
        return f"{amount:,.2f} ريال سعودي"
    else:
        return f"{amount:,.2f} دولار"

# --- دوال سيادية مستقبلية (جاهزة للتطوير) ---
# def process_commission(amount, rate=0.05):
#     """حساب عمولة المنصة (عقل المحفظة)"""
#     return amount * rate

# def log_transaction(vendor_id, amount, action_type):
#     """أرشفة التحركات المالية في السجل العام"""
#     pass
