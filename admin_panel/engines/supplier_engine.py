# admin_panel/engines/supplier_engine.py
from core.extensions import db  # 👈 التعديل الجوهري لضمان الربط مع قاعدة البيانات
from core.models.supplier import Supplier
from sqlalchemy import or_

def create_new_supplier(form_data):
    """المحرك المسؤول عن هندسة بيانات المورد الجديد مع حماية سيادية"""
    try:
        # 1. التحقق من البيانات الحساسة قبل البدء
        trade_name = form_data.get('trade_name')
        if not trade_name:
            return False, "الاسم التجاري مفقود، لا يمكن التعميد بدون اسم."

        # 2. إنشاء الكائن من البيانات الخام
        new_supplier = Supplier(
            username=form_data.get('username'),
            trade_name=trade_name,
            owner_name=form_data.get('owner_name'),
            activity_type=form_data.get('activity_type'),
            identity_type=form_data.get('identity_type'),
            phone=form_data.get('phone'),
            email=form_data.get('email'),
            bank_name=form_data.get('bank_name'),
            bank_acc=form_data.get('bank_acc'),
            province=form_data.get('province'),
            district=form_data.get('district'),
            address_detail=form_data.get('address_detail'),
            status='نشط', # قيمة افتراضية للبدء
            tier='مبتدئ'
        )

        # 3. استدعاء وظائف الموديل الذكية
        # سنضعها داخل try فرعي لضمان عدم انهيار المحرك إذا فشل توليد الكود
        try:
            if hasattr(new_supplier, 'generate_sovereign_codes'):
                new_supplier.generate_sovereign_codes()
            
            password = form_data.get('password')
            if password:
                new_supplier.set_password(password)
            else:
                new_supplier.set_password('123456')
        except Exception as tech_err:
            print(f"⚠️ خطأ فني في معالجة الموديل: {tech_err}")

        # 4. الحفظ في القاعدة (التعميد النهائي)
        db.session.add(new_supplier)
        db.session.commit()
        
        return True, new_supplier.sovereign_id if hasattr(new_supplier, 'sovereign_id') else "تم الحفظ"

    except Exception as e:
        db.session.rollback()
        print(f"❌ انهيار محرك الموردين: {str(e)}")
        return False, str(e)

def get_suppliers_by_filter(query_text=None, province=None, status=None, limit=None):
    """محرك الاستعلامات والفلترة السيادي"""
    try:
        # بناء الاستعلام الأساسي مرتباً بالأحدث
        stmt = Supplier.query.order_by(Supplier.id.desc())

        # تطبيق فلتر البحث النصي
        if query_text and query_text != "#":
            search_pattern = f"%{query_text}%"
            stmt = stmt.filter(
                or_(
                    Supplier.trade_name.like(search_pattern),
                    Supplier.owner_name.like(search_pattern),
                    Supplier.phone.like(search_pattern)
                )
            )

        # تطبيق فلتر المحافظة
        if province:
            stmt = stmt.filter(Supplier.province == province)

        # تطبيق فلتر الحالة
        if status:
            stmt = stmt.filter(Supplier.status == status)

        if limit and not (query_text or province or status):
            stmt = stmt.limit(limit)

        return stmt.all()
    except Exception as e:
        print(f"⚠️ خطأ في محرك استعلام الموردين: {e}")
        return []
