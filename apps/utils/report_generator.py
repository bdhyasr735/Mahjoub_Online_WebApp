# coding: utf-8
# 📂 apps/utils/report_generator.py

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.statement_db import SupplierStatement
from sqlalchemy import func, and_

class ReportGenerator:
    """
    مولد التقارير المركزي لمنصة محجوب أونلاين 2026.
    تم تصميم هذا الكلاس ليعمل داخل سياق التطبيق (App Context).
    """

    @staticmethod
    def _get_dynamic_attr(obj, attributes, default='---'):
        for attr in attributes:
            if hasattr(obj, attr):
                return getattr(obj, attr)
        return default

    @staticmethod
    def get_detailed_transactions(supplier_id, currency, start_date, end_date):
        # الاعتماد على db.session المتاح داخل سياق الطلب (Request Context)
        query = db.session.query(SupplierStatement)
        
        if supplier_id and supplier_id != 'ALL':
            query = query.filter(SupplierStatement.supplier_id == supplier_id)
            
        if currency and currency != 'ALL':
            query = query.filter(SupplierStatement.currency == currency)
            
        if start_date:
            query = query.filter(SupplierStatement.created_at >= start_date)
            
        if end_date:
            query = query.filter(SupplierStatement.created_at <= end_date)
            
        return query.order_by(SupplierStatement.created_at.asc()).all()

    @staticmethod
    def get_all_wallets_summary(currency):
        # استخدام Subquery لجلب الرصيد الأخير بكفاءة
        subq = db.session.query(
            SupplierStatement.supplier_id,
            func.max(SupplierStatement.created_at).label('max_date')
        ).group_by(SupplierStatement.supplier_id).subquery()

        query = db.session.query(Supplier, SupplierStatement.running_balance).join(
            subq, Supplier.id == subq.c.supplier_id
        ).join(
            SupplierStatement, and_(
                SupplierStatement.supplier_id == subq.c.supplier_id,
                SupplierStatement.created_at == subq.c.max_date
            )
        )

        if currency and currency != 'ALL':
            query = query.filter(SupplierStatement.currency == currency)
            
        data = query.all()
        
        return [{
            'trade_name': ReportGenerator._get_dynamic_attr(s[0], ['trade_name', 'name']),
            'owner_name': ReportGenerator._get_dynamic_attr(s[0], ['owner_name', 'owner']),
            'wallet_code': ReportGenerator._get_dynamic_attr(s[0], ['wallet_code', 'sovereign_id', 'code']),
            'balance': float(s[1]) if s[1] is not None else 0.0
        } for s in data]

    @staticmethod
    def calculate_net_profit(currency, start_date, end_date):
        query = db.session.query(func.sum(SupplierStatement.profit))
        
        if currency and currency != 'ALL':
            query = query.filter(SupplierStatement.currency == currency)
        
        if start_date:
            query = query.filter(SupplierStatement.created_at >= start_date)
            
        if end_date:
            query = query.filter(SupplierStatement.created_at <= end_date)
            
        result = query.scalar()
        return float(result) if result else 0.0
