# 📂 apps/utils/report_generator.py
from apps.models.statement_db import SupplierStatement # تأكد من استيراد الموديل الصحيح
from sqlalchemy import and_

class ReportGenerator:
    
    @staticmethod
    def get_detailed_transactions(supplier_id, currency, start_date, end_date):
        # بناء الفلتر الأساسي
        filters = []
        if supplier_id != 'ALL':
            filters.append(SupplierStatement.supplier_id == supplier_id)
        if currency != 'ALL':
            filters.append(SupplierStatement.currency == currency)
        if start_date:
            filters.append(SupplierStatement.created_at >= start_date)
        if end_date:
            filters.append(SupplierStatement.created_at <= end_date)
            
        return SupplierStatement.query.filter(and_(*filters)).order_by(SupplierStatement.created_at.asc()).all()

    @staticmethod
    def get_all_wallets_summary(currency):
        # هنا يتم جلب الأرصدة (يمكنك تعديل الاستعلام حسب هيكلية قاعدة بياناتك)
        # هذا مثال افتراضي لجلب ملخص لكل الموردين
        from apps.models.supplier_db import Supplier
        suppliers = Supplier.query.all()
        results = []
        for s in suppliers:
            # افتراض وجود دالة تحسب الرصيد الحالي للمورد
            results.append({
                'trade_name': s.trade_name,
                'owner_name': s.owner_name,
                'wallet_code': s.sovereign_id,
                'balance': 0.0 # قم باستبدالها بمنطق حساب الرصيد الخاص بك
            })
        return results

    @staticmethod
    def calculate_net_profit(currency, start_date, end_date):
        # منطق حساب الأرباح
        return 0.0
