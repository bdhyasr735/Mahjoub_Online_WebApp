# coding: utf-8
# 📂 apps/utils/report_generator.py
from sqlalchemy import func
from apps.extensions import db
from apps.models.statement_db import SupplierStatement
from apps.models.wallet_db import WalletTransaction

class ReportGenerator:
    """
    محرك مركزي آمن لاستخراج التقارير المالية - منصة محجوب أونلاين
    """

    @staticmethod
    def get_platform_financial_tree(currency='ALL', start_date=None, end_date=None):
        """ استخراج شجرة حسابات المنصة ومجاميع الحركات حسب العملة """
        query = db.session.query(
            SupplierStatement.currency, 
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
        """ 
        استخراج الحركات التفصيلية لمورد معين 
        🛡️ تم تعديل الاستعلام لتجنب الحقول الناقصة في قاعدة البيانات (reference_number & notes) لتفادي الانهيار تماماً.
        """
        
        # نطلب فقط الأعمدة الأساسية المتواجدة والمستقرة في قاعدة البيانات الفورية
        query = db.session.query(
            SupplierStatement.id,
            SupplierStatement.supplier_id,
            SupplierStatement.created_at,
            SupplierStatement.description,
            SupplierStatement.currency,
            SupplierStatement.debit,
            SupplierStatement.credit,
            SupplierStatement.running_balance
        )
        
        if supplier_id:
            query = query.filter(SupplierStatement.supplier_id == supplier_id)
        if currency and currency != 'ALL':
            query = query.filter(SupplierStatement.currency == currency)
        if start_date:
            query = query.filter(SupplierStatement.created_at >= start_date)
        if end_date:
            query = query.filter(SupplierStatement.created_at <= end_date)
            
        results = query.order_by(SupplierStatement.created_at.desc()).all()

        # بناء البيانات برمجياً وحقن الحقول الناقصة بقيم آمنة متوافقة مع الـ HTML والـ Routes
        statements = []
        for r in results:
            s = SupplierStatement()
            s.id = r.id
            s.supplier_id = r.supplier_id
            s.created_at = r.created_at
            s.description = r.description
            s.currency = r.currency
            s.debit = r.debit
            s.credit = r.credit
            s.running_balance = r.running_balance
            
            # حقن الحقول غير الموجودة بقيم افتراضية نظيفة لمنع خطأ الـ AttributeError أو الـ UndefinedColumn
            s.reference_number = "---"
            s.notes = "---"
            
            statements.append(s)

        return statements

    @staticmethod
    def calculate_net_profit(currency, start_date=None, end_date=None):
        """ حساب صافي أرباح المنصة من المحفظة المالية """
        query = WalletTransaction.query
        
        if currency and currency != 'ALL':
            query = query.filter(WalletTransaction.currency == currency)
        if start_date:
            query = query.filter(WalletTransaction.created_at >= start_date)
        if end_date:
            query = query.filter(WalletTransaction.created_at <= end_date)
            
        total_profit = query.with_entities(func.sum(WalletTransaction.profit_margin)).scalar()
        return float(total_profit or 0)
