# coding: utf-8
# 🔑 سكريبت ترقيع وتعميد المحافظ للموردين السابقين - منصة محجوب أونلاين 2026

import os
import sys

# إضافة المسار الرئيسي للمشروع لضمان التعرف على حزمة apps بأمان
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from apps import create_app, db
from apps.models import Supplier
from apps.models.wallet_db import Wallet

# 1. تهيئة سياق التطبيق (App Context) لربط السكريبت بمحرك الـ Flask المركزي وقاعدة البيانات
app = create_app()

def migrate_old_suppliers_wallets():
    with app.app_context():
        print("\n⏳ [منصة محجوب أونلاين] جاري فحص الموردين السابقين وتوليد المحافظ السيادية الموحدة...")
        
        try:
            # 2. سحب جميع الموردين المسجلين في النظام
            all_suppliers = Supplier.query.all()
            counter = 0

            for supplier in all_suppliers:
                # الفحص والتحقق لمنع تكرار إنشاء محفظة لمورد يمتلك واحدة بالفعل في الجدول
                existing_wallet = Wallet.query.filter_by(supplier_id=supplier.id).first()
                
                if not existing_wallet:
                    # 3. بناء المحفظة وتصفير العملات الثلاث للمورد السابق (ريال يمني، ريال سعودي، دولار أمريكي)
                    new_wallet = Wallet(
                        supplier_id=supplier.id,
                        # wallet_number=supplier.sovereign_id, # ألغِ التعليق (#) فقط إذا كان عمود رقم المحفظة مضافاً مادياً في الـ Wallet model
                        yer_total=0.0, yer_available=0.0, yer_pending=0.0, yer_withdrawn=0.0,
                        sar_total=0.0, sar_available=0.0, sar_pending=0.0, sar_withdrawn=0.0,
                        usd_total=0.0, usd_available=0.0, usd_pending=0.0, usd_withdrawn=0.0
                    )
                    db.session.add(new_wallet)
                    counter += 1
                    print(f"   ✅ تم توليد محفظة موحدة للمورد: {supplier.username} | المعرف: {supplier.sovereign_id}")

            # 4. حفظ وتعميد كافة المحافظ الجديدة في قاعدة البيانات دفعة واحدة (Commit)
            if counter > 0:
                db.session.commit()
                print(f"\n🎉 [اكتمل التعميد] تم بنجاح حقن وتنشيط ({counter}) محفظة مالية جديدة للموردين السابقين!")
            else:
                print("\n✨ [حالة مستقرة] جميع الموردين السابقين يمتلكون محافظ مفعلة مسبقاً، لا توجد فجوات مادية في النظام.")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ [خطأ حوكمي] فشلت عملية الترقيع بسبب: {str(e)}")

if __name__ == "__main__":
    migrate_old_suppliers_wallets()
