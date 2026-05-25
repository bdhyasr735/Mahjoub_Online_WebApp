# coding: utf-8
# 📂 apps/utils/report_generator.py
# ⚙️ محرك التقارير المركزية وشجرة الحسابات - منصة محجوب أونلاين 2026

from sqlalchemy import func
from apps.models.statement_db import SupplierStatement
from apps.models.wallet_db import WalletTransaction

class ReportGenerator:
    """
    محرك مركزي لاستخراج التقارير المالية.
    يتم استخدامه في اللوحة المركزية وفي صفحات كشوفات الموردين.
    """

    @staticmethod
    def get_platform_financial_tree(currency='ALL', start_date=None, end_date=None):
        """
        استخراج شجرة حسابات المنصة (إجمالي وتفصيلي) حسب نوع الحركة.
        تستخدم هذه الدالة لتوليد التقارير المالية للمنصة.
        """
        query = db.session.query(
            SupplierStatement.reference_type,
            func.sum(SupplierStatement.debit).label('total_debit'),
            func.sum(SupplierStatement.credit).label('total_credit')
        )

        # تطبيق الفلاتر
        if currency != 'ALL':
            query = query.filter_by(currency=currency)
        if start_date:
            query = query.filter(SupplierStatement.created_at >= start_date)
        if end_date:
            query = query.filter(SupplierStatement.created_at <= end_date)
            
        results = query.group_by(SupplierStatement.reference_type).all()
        
        return [
            {
                'type': r.reference_type,
                'debit': float(r.total_debit or 0),
                'credit': float(r.total_credit or 0),
                'balance': float((r.total_credit or 0) - (r.total_debit or 0))
            } for r in results
        ]

    @staticmethod
    def get_detailed_transactions(supplier_id=None, currency='ALL', start_date=None, end_date=None):
        """
        استخراج الحركات التفصيلية لمورد معين أو للمنصة بالكامل.
        """
        query = SupplierStatement.query
        
        if supplier_id:
            query = query.filter_by(supplier_id=supplier_id)
        if currency != 'ALL':
            query = query.filter_by(currency=currency)
        if start_date:
            query = query.filter(SupplierStatement.created_at >= start_date)
        if end_date:
            query = query.filter(SupplierStatement.created_at <= end_date)
            
        return query.order_by(SupplierStatement.created_at.desc()).all()

    @staticmethod
    def calculate_net_profit(currency, start_date=None, end_date=None):
        """
        حساب صافي أرباح المنصة (شجرة الحسابات الربحية).
        """
        query = WalletTransaction.query.filter_by(currency=currency)
        if start_date:
            query = query.filter(WalletTransaction.created_at >= start_date)
        if end_date:
            query = query.filter(WalletTransaction.created_at <= end_date)
            
        total_profit = query.with_entities(func.sum(WalletTransaction.profit_margin)).scalar()
        return float(total_profit or 0)
