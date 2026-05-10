@staticmethod
    def approve_supplier(sup_id):
        from core.models.supplier import Supplier
        supplier = Supplier.query.get(sup_id)
        if supplier:
            supplier.status = 'active'
            db.session.commit()
            return True, "تم تعميد المورد بنجاح"
        return False, "المورد غير موجود"

    @staticmethod
    def search_suppliers(query, status_filter):
        from core.models.supplier import Supplier
        q = Supplier.query
        if query:
            q = q.filter(Supplier.trade_name.contains(query))
        if status_filter:
            q = q.filter(Supplier.status == status_filter)
        return q.all()
