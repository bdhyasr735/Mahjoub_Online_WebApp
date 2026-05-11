# core/services/supplier_service.py
from core import db
from core.models.supplier import Supplier
import logging

# إعداد السجلات لمراقبة العمليات في Railway وتتبع الأخطاء بدقة
logger = logging.getLogger(__name__)

def get_all_suppliers():
    """
    جلب كافة الموردين مع إحصائياتهم للوحة التحكم.
    يتم استدعاؤها في admin_panel/routes.py لملء جداول الحوكمة.
    """
    try:
        suppliers = Supplier.query.order_by(Supplier.id.desc()).all()
        # حساب الإحصائيات السيادية للعرض العلوي
        stats = {
            'total': len(suppliers),
            'active': Supplier.query.filter_by(status='active').count(),
            'sovereign': Supplier.query.filter_by(tier='سيادي').count(),
            'total_yer': db.session.query(db.func.sum(Supplier.balance_yer)).scalar() or 0
        }
        return {'suppliers': suppliers, 'stats': stats}
    except Exception as e:
        logger.error(f"خطأ في جلب بيانات الموردين: {str(e)}")
        return {'suppliers': [], 'stats': {'total': 0, 'active': 0, 'sovereign': 0, 'total_yer': 0}}

def create_supplier(data):
    """
    محرك أرشفة الموردين: يقوم بالتحقق، التشفير، وتوليد الأكواد السيادية.
    """
    try:
        # 1. إنشاء كائن المورد بالمسميات الصحيحة للموديل
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
            address_detail=data.get('address_detail'),
            bank_name=data.get('bank_name'),
            bank_acc=data.get('bank_acc'),
            status='active',
            tier=data.get('tier', 'مبتدئ')
        )
        
        # 2. تأمين كلمة المرور
        password = data.get('password') or '123456'
        new_supplier.set_password(password)
        
        # 3. توليد الأكواد السيادية (SUP-MHA)
        new_supplier.generate_sovereign_codes()
        
        # 4. تنفيذ الحفظ في قاعدة البيانات
        db.session.add(new_supplier)
        db.session.commit()
        
        return True, new_supplier.trade_name
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"فشل بروتوكول التعميد: {str(e)}")
        return False, str(e)

def update_supplier_profile(supplier_id, data):
    """
    بروتوكول تحديث بيانات الكيان: يسمح بتعديل المعلومات اللوجستية والشخصية 
    ويمنع منعاً باتاً تعديل الأرصدة أو المعرفات السيادية من هذه الدالة.
    """
    try:
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return False, "الكيان المستهدف غير موجود في السجلات"

        # تحديث الحقول المسموح بها فقط (الحوكمة اللوجستية)
        supplier.trade_name = data.get('trade_name', supplier.trade_name)
        supplier.owner_name = data.get('owner_name', supplier.owner_name)
        supplier.email = data.get('email', supplier.email)
        supplier.phone = data.get('phone', supplier.phone)
        
        # يمكن إضافة تحديث الصورة هنا مستقبلاً
        if 'identity_image' in data:
            supplier.identity_image = data.get('identity_image')

        db.session.commit()
        logger.info(f"تم تعميد تعديل بيانات الكيان: {supplier.trade_name}")
        return True, "تم تحديث بيانات الكيان بنجاح"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"فشل تحديث بيانات المورد {supplier_id}: {str(e)}")
        return False, str(e)

def get_next_supplier_id():
    """
    حساب المعرف القادم لعرضه في واجهة 'تعميد كيان جديد'.
    """
    try:
        last_sup = Supplier.query.order_by(Supplier.id.desc()).first()
        return (last_sup.id + 1) if last_sup else 1
    except Exception:
        return 1
