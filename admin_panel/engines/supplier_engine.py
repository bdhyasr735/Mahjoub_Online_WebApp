# admin_panel/engines/supplier_engine.py
from core.extensions import db
from core.models.supplier import Supplier
from sqlalchemy import or_
import uuid

def create_new_supplier(form_data):
    """المحرك السيادي - نسخة استئصال الأخطاء v4.6 (المتوافقة مع التحديثات المركزية)"""
    try:
        # 1. طباعة البيانات المستلمة للمراقبة
        print(f"📡 محاولة تعميد مورد جديد: {form_data.get('trade_name')}")

        # 2. إنشاء الكيان مع استيعاب الحقول الجديدة التي أضفناها في الهيكل
        new_supplier = Supplier(
            username=form_data.get('username') or f"sup_{form_data.get('phone')}_{uuid.uuid4().hex[:4]}",
            trade_name=form_data.get('trade_name'),
            owner_name=form_data.get('owner_name'),
            phone=form_data.get('phone'),
            email=form_data.get('email'),
            province=form_data.get('province'),
            district=form_data.get('district'),
            address_detail=form_data.get('address_detail'),
            activity_type=form_data.get('activity_type'),
            identity_type=form_data.get('identity_type'),
            bank_name=form_data.get('bank_name'),
            bank_acc=form_data.get('bank_acc'),
            status='نشط',
            tier='مبتدئ'
        )

        # 3. معالجة كلمة المرور (تأمين الحساب)
        password = form_data.get('password') or '123456'
        if hasattr(new_supplier, 'set_password'):
            new_supplier.set_password(password)

        # 4. توليد المعرف السيادي (Sovereign ID)
        try:
            if hasattr(new_supplier, 'generate_sovereign_codes'):
                new_supplier.generate_sovereign_codes()
            else:
                new_supplier.sovereign_id = f"MAH-{uuid.uuid4().hex[:8].upper()}"
        except Exception as e:
            print(f"⚠️ تنبيه في توليد الكود: {e}")
            new_supplier.sovereign_id = f"MAH-TMP-{uuid.uuid4().hex[:6].upper()}"

        # 5. الحفظ النهائي في الترسانة
        db.session.add(new_supplier)
        db.session.commit()
        
        return True, new_supplier.sovereign_id

    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        print(f"❌ انهيار المحرك السيادي: {error_msg}")
        return False, error_msg

def get_suppliers_by_filter(query_text=None, province=None, status=None, limit=None):
    """محرك البحث والفلترة السيادي"""
    try:
        stmt = Supplier.query.order_by(Supplier.id.desc())

        if query_text and query_text != "#":
            search_pattern = f"%{query_text}%"
            stmt = stmt.filter(
                or_(
                    Supplier.trade_name.like(search_pattern),
                    Supplier.owner_name.like(search_pattern),
                    Supplier.phone.like(search_pattern),
                    Supplier.sovereign_id.like(search_pattern)
                )
            )

        if province:
            stmt = stmt.filter(Supplier.province == province)
        if status:
            stmt = stmt.filter(Supplier.status == status)
        if limit:
            stmt = stmt.limit(limit)

        return stmt.all()
    except Exception as e:
        print(f"⚠️ خطأ في استعلام الموردين: {e}")
        return []
