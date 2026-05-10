# admin_panel/suppliers_logic.py
from core import db
from core.models.supplier import Supplier, archive_sys

class SupplierLogic:
    @staticmethod
    def get_next_id():
        """توليد المعرف السيادي القادم تلقائياً"""
        last = Supplier.query.order_by(Supplier.id.desc()).first()
        # نبدأ من 100 إذا كانت قاعدة البيانات فارغة
        next_num = (last.id + 1) if last else 100
        return f"SUP_{next_num}#"

    @staticmethod
    def commit_new_supplier(form_data):
        """تنفيذ عملية التعميد المركزية وتصحيح الحقول"""
        try:
            # نقوم ببناء الكيان باستخدام الحقول الأساسية فقط المعرفة في الموديل
            new_sup = Supplier(
                sovereign_id=SupplierLogic.get_next_id(),
                trade_name=form_data.get('trade_name'),
                owner_name=form_data.get('owner_name'),
                province=form_data.get('province'),
                district=form_data.get('district'),
                phone=form_data.get('phone'),
                tier=form_data.get('tier', 'مبتدئ'), # التأكد من وجود قيمة افتراضية
                # تصفير المحفظة الثلاثية تلقائياً كما اتفقنا
                balance_yer=0.0,
                balance_sar=0.0,
                balance_usd=0.0,
                status='active'
            )
            
            # ملاحظة: تأكدنا من عدم وجود 'identity_type' هنا لأنه سبب الخطأ
            
            db.session.add(new_sup)
            db.session.commit()
            
            # الأرشفة السيادية في GitHub بعد نجاح الحفظ في Postgres
            try:
                archive_sys.archive_entity(new_sup)
            except Exception as archive_err:
                # إذا فشلت الأرشفة لا نعطل العملية بل نسجل تحذير
                print(f"Warning: Archive failed: {str(archive_err)}")
            
            return True, "تم تعميد الكيان بنجاح وأرشفته سيادياً."
            
        except Exception as e:
            db.session.rollback()
            # هذا ما يظهر لك في السجلات الآن
            print(f"ERROR:Supplier_Engine: فشل التعميد: {str(e)}")
            return False, f"فشلت عملية التعميد: {str(e)}"
