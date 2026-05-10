# admin_panel/suppliers_logic.py
from core import db
from core.models.supplier import Supplier

class SupplierLogic:
    @staticmethod
    def register_supplier(form_data):
        """محرك تعميد الموردين: تنفيذ عمليات الحفظ في قاعدة البيانات"""
        try:
            # 1. توليد المعرف السيادي القادم
            last_id = db.session.query(db.func.max(Supplier.id)).scalar() or 0
            new_sovereign_id = f"SUP_{last_id + 1}#"

            # 2. إنشاء الكيان الجديد
            new_supplier = Supplier(
                sovereign_id=new_sovereign_id,
                trade_name=form_data.get('trade_name'),
                owner_name=form_data.get('owner_name'),
                activity_type=form_data.get('activity_type'),
                identity_type=form_data.get('identity_type'),
                province=form_data.get('province'),
                district=form_data.get('district'),
                address_detail=form_data.get('address_detail'),
                phone=form_data.get('phone'),
                bank_name=form_data.get('bank_name'),
                bank_acc=form_data.get('bank_acc'),
                status='active'
            )

            db.session.add(new_supplier)
            db.session.commit()
            return True, f"تم تعميد المورد {new_supplier.trade_name} بنجاح برقم {new_sovereign_id}"

        except Exception as e:
            db.session.rollback()
            return False, f"فشل في التعميد: {str(e)}"

    @staticmethod
    def get_next_id():
        """توليد المعرف التالي لإظهاره في الواجهة"""
        last_id = db.session.query(db.func.max(Supplier.id)).scalar() or 0
        return f"SUP_{last_id + 1}#"

    @staticmethod
    def search_suppliers(query=None, status=None):
        """محرك البحث في الرادار"""
        s_query = Supplier.query
        if query:
            s_query = s_query.filter(
                (Supplier.trade_name.contains(query)) | 
                (Supplier.sovereign_id.contains(query))
            )
        if status:
            s_query = s_query.filter_by(status=status)
            
        return s_query.order_by(Supplier.created_at.desc()).all()
