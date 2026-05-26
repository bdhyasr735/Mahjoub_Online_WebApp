# coding: utf-8
# 📂 apps/utils/report_generator.py

from apps.models.supplier_db import Supplier
from apps.models.statement_db import SupplierStatement
from sqlalchemy import and_, func

class ReportGenerator:

    @staticmethod
    def get_detailed_transactions(supplier_id, currency, start_date, end_date):
        """جلب كشف الحساب التفصيلي بناءً على الفلاتر"""
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
        """جلب ملخص أرصدة جميع الموردين"""
        suppliers = Supplier.query.all()
        results = []
        
        for s in suppliers:
            # فلترة إضافية حسب العملة إذا كانت محددة
            query = SupplierStatement.query.filter_by(supplier_id=s.id)
            if currency != 'ALL':
                query = query.filter_by(currency=currency)
                
            last_statement = query.order_by(SupplierStatement.created_at.desc()).first()
            
            balance = last_statement.running_balance if last_statement else 0.0
            
            results.append({
                'trade_name': getattr(s, 'trade_name', '---'),
                'owner_name': getattr(s, 'owner_name', '---'),
                'wallet_code': getattr(s, 'sovereign_id', '---'),
                'balance': float(balance)
            })
        return results

    @staticmethod
    def calculate_net_profit(currency, start_date, end_date):
        """حساب إجمالي الأرباح في الفترة المحددة"""
        # يمكنك إضافة منطق حساب الأرباح الخاص بك هنا
        return 0.0
