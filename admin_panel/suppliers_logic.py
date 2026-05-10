# admin_panel/suppliers_logic.py
from core import db
from core.models.supplier import Supplier
import logging

logger = logging.getLogger("Supplier_Engine")

class SupplierLogic:
    """ محرك الحوكمة لتعميد وإدارة الموردين - محجوب أونلاين v3.5 """

    @staticmethod
    def get_next_id():
        """توليد معرف سيادي تلقائي (SUP_1#)"""
        last = Supplier.query.order_by(Supplier.id.desc()).first()
        return f"SUP_{last.id + 1}#" if last else "SUP_1#"

    @staticmethod
    def register_supplier(data):
        """تعميد مورد جديد وضبط المحفظة الثلاثية"""
        try:
            new_sup = Supplier(
                trade_name=data.get('trade_name'),
                phone=data.get('phone'),
                identity_type=data.get('identity_type'),
                sovereign_id=data.get('sovereign_id'),
                status='active',
                tier='مورد معتمد',
                # تصفير الأرصدة السيادية عند التأسيس
                balance_yer=0.0, balance_sar=0.0, balance_usd=0.0
            )
            db.session.add(new_sup)
            db.session.commit()
            return True, f"تم تعميد الكيان {new_sup.trade_name} بنجاح"
        except Exception as e:
            db.session.rollback()
            logger.error(f"فشل التعميد: {str(e)}")
            return False, "خطأ في البيانات أو الكيان موجود مسبقاً"

    @staticmethod
    def search_suppliers(query=None, status_filter=None):
        """الرادار الذكي للبحث عن الموردين"""
        q = Supplier.query
        if query:
            q = q.filter(Supplier.trade_name.contains(query))
        if status_filter:
            q = q.filter(Supplier.status == status_filter)
        return q.order_by(Supplier.id.desc()).all()

    @staticmethod
    def update_balance(sup_id, amount, currency):
        """تحديث رصيد مورد (YER/SAR/USD)"""
        try:
            sup = Supplier.query.get(sup_id)
            field = f'balance_{currency.lower()}'
            if hasattr(sup, field):
                setattr(sup, field, getattr(sup, field) + float(amount))
                db.session.commit()
                return True, "تم تحديث الخزينة"
            return False, "عملة غير مدعومة"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
