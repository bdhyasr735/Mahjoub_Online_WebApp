# core/services/supplier_service.py
from core import db
from core.models.supplier import Supplier
import logging

# إعداد السجلات (Logs) لمراقبة العمليات السيادية وتسهيل التنقيح في بيئة الإنتاج
logger = logging.getLogger(__name__)

def get_all_suppliers():
    """
    جلب كافة الموردين مع إحصائياتهم للوحة التحكم.
    تستخدم لتغذية جداول الحوكمة بالبيانات اللحظية للرادار.
    """
    try:
        suppliers = Supplier.query.order_by(Supplier.id.desc()).all()
        
        # حساب الإحصائيات السيادية للعرض في واجهة الرادار
        # تم استخدام الاستعلامات المباشرة (Queries) لضمان دقة الأرقام المالية
        stats = {
            'total': len(suppliers),
            'active': Supplier.query.filter_by(status='active').count(),
            'sovereign': Supplier.query.filter_by(tier='سيادي').count(),
            'total_yer': db.session.query(db.func.sum(Supplier.balance_yer)).scalar() or 0
        }
        return {'suppliers': suppliers, 'stats': stats}
    except Exception as e:
        logger.error(f"⚠️ خطأ سيادي في استرجاع قائمة الموردين: {str(e)}")
        return {'suppliers': [], 'stats': {'total': 0, 'active': 0, 'sovereign': 0, 'total_yer': 0}}

def create_supplier(data):
    """
    محرك تعميد الموردين الجدد: يقوم بالتحقق، التشفير، وتوليد الأكواد الرقمية.
    """
    try:
        # 1. بناء كائن المورد وتسكين البيانات في الحقول المخصصة (الترسانة الأساسية)
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
        
        # 2. تأمين الولوج بكلمة مرور افتراضية (بروتوكول الأمان الأولي)
        password = data.get('password') or '123456'
        new_supplier.set_password(password)
        
        # 3. توليد الهوية الرقمية السيادية (SUP-MHA-XXXX) عبر موديل المورد
        new_supplier.generate_sovereign_codes()
        
        # 4. تعميد البيانات في القاعدة الرئيسية
        db.session.add(new_supplier)
        db.session.commit()
        
        logger.info(f"✅ تم تعميد كيان جديد بنجاح: {new_supplier.trade_name}")
        return True, new_supplier.trade_name
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ فشل بروتوكول إضافة المورد: {str(e)}")
        return False, str(e)

def update_supplier_profile(supplier_id, data):
    """
    بروتوكول تحديث بيانات الكيان اللوجستية والشخصية.
    يضمن حماية الأرصدة والهوية السيادية من التعديل العشوائي عبر الروابط.
    """
    try:
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return False, "عذراً، لم يتم العثور على الكيان في السجلات المركزية."

        # تحديث الحقول المسموح بها فقط (حوكمة البيانات اللوجستية)
        supplier.trade_name = data.get('trade_name', supplier.trade_name)
        supplier.owner_name = data.get('owner_name', supplier.owner_name)
        supplier.email = data.get('email', supplier.email)
        supplier.phone = data.get('phone', supplier.phone)
        
        # إدارة تحديث الصورة التعريفية السيادية في حال وجودها
        if 'identity_image' in data and data['identity_image']:
            supplier.identity_image = data.get('identity_image')

        # تعميد التعديلات نهائياً في الترسانة الرقمية
        db.session.commit()
        logger.info(f"⚙️ تم تحديث بروفايل الكيان: {supplier.trade_name}")
        return True, "تم تحديث بيانات الكيان بنجاح."
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"⚠️ فشل تحديث بيانات المورد {supplier_id}: {str(e)}")
        return False, str(e)

def get_next_supplier_id():
    """
    حساب الرقم التسلسلي القادم لعرضه في واجهة الإضافة (Predictive ID).
    """
    try:
        last_sup = Supplier.query.order_by(Supplier.id.desc()).first()
        return (last_sup.id + 1) if last_sup else 1
    except Exception:
        return 1
