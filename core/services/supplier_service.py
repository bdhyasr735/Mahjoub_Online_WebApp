# core/services/supplier_service.py
from core import db
from core.models.supplier import Supplier
import logging

# إعداد السجلات لمراقبة العمليات في Railway
logger = logging.getLogger(__name__)

def get_all_suppliers():
    """
    جلب كافة الموردين مع إحصائياتهم للوحة التحكم.
    يتم استدعاؤها في admin_panel/routes.py
    """
    try:
        suppliers = Supplier.query.order_by(Supplier.id.desc()).all()
        stats = {
            'total': len(suppliers),
            'active': Supplier.query.filter_by(status='active').count(),
            'sovereign': Supplier.query.filter_by(tier='سيادي').count()
        }
        return {'suppliers': suppliers, 'stats': stats}
    except Exception as e:
        logger.error(f"خطأ في جلب بيانات الموردين: {str(e)}")
        return {'suppliers': [], 'stats': {'total': 0, 'active': 0, 'sovereign': 0}}

def create_supplier(data):
    """
    محرك أرشفة الموردين: يقوم بالتحقق، التشفير، وتوليد الأكواد السيادية.
    """
    try:
        # 1. إنشاء كائن المورد بالمسميات الصحيحة للموديل
        new_supplier = Supplier(
            username=data.get('username'),
            trade_name=data.get('trade_name'), # الحقل الصحيح في الموديل
            owner_name=data.get('owner_name'),
            activity_type=data.get('activity_type'),
            identity_type=data.get('identity_type'),
            phone=data.get('phone'),
            email=data.get('email'),
            province=data.get('province'),
            district=data.get('district'),
            address_detail=data.get('address_detail'),
            bank_name=data.get('bank_name'),
            bank_acc=data.get('bank_acc'),
            status='active',
            tier=data.get('tier', 'مبتدئ')
        )
        
        # 2. تأمين كلمة المرور (باستخدام الدالة المعرفة في الموديل)
        password = data.get('password') or '123456'
        new_supplier.set_password(password)
        
        # 3. توليد الأكواد السيادية (SUP-MHA) 
        # ملاحظة: تم استخدام generate_sovereign_codes بدلاً من المسمى الخاطئ mint_id
        new_supplier.generate_sovereign_codes()
        
        # 4. تنفيذ الحفظ في قاعدة البيانات
        db.session.add(new_supplier)
        db.session.commit()
        
        return True, new_supplier.trade_name
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"فشل بروتوكول التعميد: {str(e)}")
        return False, str(e)

def get_next_supplier_id():
    """
    حساب المعرف القادم لعرضه في واجهة 'تعميد كيان جديد'.
    """
    try:
        last_sup = Supplier.query.order_by(Supplier.id.desc()).first()
        return (last_sup.id + 1) if last_sup else 1
    except:
        return 1
