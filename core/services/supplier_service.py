# core/services/supplier_service.py
from core import db
from core.models.supplier import Supplier, SupplierStaff
from core.models.user import User
import logging

logger = logging.getLogger(__name__)

def get_all_suppliers():
    """ جلب كافة الموردين مع إحصائياتهم للوحة التحكم """
    try:
        suppliers = Supplier.query.order_by(Supplier.id.desc()).all()
        stats = {
            'total': len(suppliers),
            'active': Supplier.query.filter_by(status='active').count(),
            'sovereign': Supplier.query.filter_by(tier='سيادي').count(),
            'total_yer': db.session.query(db.func.sum(Supplier.balance_yer)).scalar() or 0
        }
        return {'suppliers': suppliers, 'stats': stats}
    except Exception as e:
        logger.error(f"⚠️ خطأ في استرجاع قائمة الموردين: {str(e)}")
        return {'suppliers': [], 'stats': {'total': 0, 'active': 0, 'sovereign': 0, 'total_yer': 0}}

def create_supplier(data):
    """ محرك تعميد الموردين الجدد """
    try:
        new_supplier = Supplier(
            username=data.get('username'),
            trade_name=data.get('trade_name'),
            owner_name=data.get('owner_name'),
            activity_type=data.get('activity_type'),
            identity_type=data.get('identity_type'),
            phone=data.get('phone'),
            email=data.get('email'),
            province=data.get('province'),
            district=data.get('district'),
            status='active',
            tier=data.get('tier', 'مبتدئ')
        )
        password = data.get('password') or '123456'
        new_supplier.set_password(password)
        
        # توليد المعرفات السيادية (SUP-MHA & WEL-MAH)
        new_supplier.generate_sovereign_codes()
        
        db.session.add(new_supplier)
        db.session.commit()
        logger.info(f"✅ تم تعميد كيان جديد: {new_supplier.trade_name}")
        return True, new_supplier.trade_name
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def update_supplier_field(supplier_id, field, value):
    """ بروتوكول الحفظ التلقائي - تحديث حقل واحد فقط لسرعة الأداء """
    try:
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return False, "الكيان غير موجود"
        
        if hasattr(supplier, field):
            setattr(supplier, field, value)
            db.session.commit()
            return True, "تم التعميد بنجاح"
        return False, "الحقل غير موجود"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def add_staff_to_supplier(supplier_id, staff_data):
    """ نظام إضافة موظفين تابعين لكيان المورد """
    try:
        # التحقق من عدم تكرار اسم المستخدم في نظام المستخدمين العام
        existing = User.query.filter_by(username=staff_data.get('username')).first()
        if existing:
            return False, "اسم المستخدم محجوز مسبقاً"

        new_staff = User(
            username=staff_data.get('username'),
            full_name=staff_data.get('name'),
            role='employee', # رتبة موظف مورد
            supplier_id=supplier_id
        )
        new_staff.set_password(staff_data.get('password'))
        
        db.session.add(new_staff)
        db.session.commit()
        return True, "تم إضافة الموظف لطاقم العمل"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def get_next_supplier_id():
    """ حساب الرقم التسلسلي القادم """
    try:
        last_sup = Supplier.query.order_by(Supplier.id.desc()).first()
        return (last_sup.id + 1) if last_sup else 1
    except Exception:
        return 1
