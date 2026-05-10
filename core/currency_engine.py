# core/currency_engine.py
from decimal import Decimal

class CurrencyEngine:
    def __init__(self):
        # أسعار افتراضية للطوارئ (Fallback Rates)
        self.default_rates = {
            'SAR_TO_YER': Decimal('530.0'), 
            'USD_TO_YER': Decimal('1600.0'),
            'MARKUP': Decimal('0.10')  # 10%
        }

    def get_live_rates(self):
        """
        جلب أسعار الصرف من قاعدة البيانات (مستقبلاً) 
        أو إرجاع القيم الافتراضية حالياً.
        """
        # ملاحظة للمؤسس علي: هنا سنربط لاحقاً بجدول Settings في قاعدة البيانات
        return self.default_rates

    def convert_to_yer(self, amount, from_currency):
        """تحويل أي مبلغ إلى الريال اليمني (العملة المرجعية للنظام)"""
        rates = self.get_live_rates()
        amount = Decimal(str(amount))
        
        if from_currency == 'SAR':
            return amount * rates['SAR_TO_YER']
        elif from_currency == 'USD':
            return amount * rates['USD_TO_YER']
        return amount

    def calculate_final_price(self, base_price, supplier_markup=0):
        """
        حساب السعر النهائي للمستهلك (سعر محجوب أونلاين السيادي)
        السعر = (سعر المورد + عمولة المنصة) + هامش ربح المورد الإضافي
        """
        rates = self.get_live_rates()
        base_price = Decimal(str(base_price))
        supplier_markup = Decimal(str(supplier_markup))
        
        platform_fee = base_price * rates['MARKUP']
        final_price = base_price + platform_fee + supplier_markup
        
        return round(float(final_price), 2)

    def get_formatted_price(self, amount, currency='YER'):
        """تنسيق السعر للعرض في الواجهة الأمامية"""
        return f"{amount:,.2f} {currency}"

# تصدير المحرك للاستخدام الفوري في الإدارة والموقع
currency_engine = CurrencyEngine()
