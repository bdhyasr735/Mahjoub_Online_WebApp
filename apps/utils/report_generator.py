# coding: utf-8
# 📂 apps/utils/report_generator.py
from sqlalchemy import func
from apps.extensions import db
from apps.models.statement_db import SupplierStatement
from apps.models.wallet_db import WalletTransaction

class ReportGenerator:
    """
    محرك مركزي لاستخراج التقارير المالية - منصة محجوب أونلاين
    """

    @staticmethod
    def get_platform_financial_tree(currency='ALL', start_date=None, end_date=None):
        """ استخراج شجرة حسابات المنصة ومجاميع الحركات حسب العملة """
        query = db.session.query(
            SupplierStatement.currency, # التجميع حسب العملة لضمان توافق الحقول
            func.sum(SupplierStatement.debit).label('total_debit'),
            func.sum(SupplierStatement.credit).label('total_credit')
        )

        if currency and currency != 'ALL':
            query = query.filter(SupplierStatement.currency == currency)
        if start_date:
            query = query.filter(SupplierStatement.created_at >= start_date)
        if end_date:
            query = query.filter(SupplierStatement.created_at <= end_date)
            
        results = query.group_by(SupplierStatement.currency).all()
        
        return [
            {
                'type': r.currency,
                'debit': float(r.total_debit or 0),
                'credit': float(r.total_credit or 0),
                'balance': float((r.total_credit or 0) - (r.total_debit or 0))
            } for r in results
        ]

    @staticmethod
    def get_detailed_transactions(supplier_id=None, currency='ALL', start_date=None, end_date=None):
        """ استخراج الحركات التفصيلية لمورد معين بشكل منظم """
        query = SupplierStatement.query
        
        if supplier_id:
            query = query.filter(SupplierStatement.supplier_id == supplier_id)
        if currency and currency != 'ALL':
            query = query.filter(SupplierStatement.currency == currency)
        if start_date:
            query = query.filter(SupplierStatement.created_at >= start_date)
        if end_date:
            query = query.filter(SupplierStatement.created_at <= end_date)
            
        return query.order_by(SupplierStatement.created_at.desc()).all()

    @staticmethod
    def calculate_net_profit(currency, start_date=None, end_date=None):
        """ حساب صافي أرباح المنصة من المحفظة المالية """
        query = WalletTransaction.query
        
        # إذا تم اختيار كل العملات، نتجنب دمج أرقام عملات مختلفة حسابياً
        if currency and currency != 'ALL':
            query = query.filter(WalletTransaction.currency == currency)
        if start_date:
            query = query.filter(WalletTransaction.created_at >= start_date)
        if end_date:
            query = query.filter(WalletTransaction.created_at <= end_date)
            
        total_profit = query.with_entities(func.sum(WalletTransaction.profit_margin)).scalar()
        return float(total_profit or 0)
