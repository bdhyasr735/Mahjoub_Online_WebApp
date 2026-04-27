import os
from core import create_app, db
from core.models import User, Supplier, Product
from werkzeug.security import generate_password_hash

# 1. إنشاء تطبيق Flask بالهوية السيادية الموحدة
app = create_app()

def initialize_sovereign_system():
    """
    وظيفة التطهير والتعميد: لإعادة بناء قاعدة البيانات 
    وضمان مطابقة الكود للواقع التقني الجديد والمحافظ المالية.
    """
    with app.app_context():
        try:
            print("🔄 [System] جاري تطهير وإعادة بناء الهيكل السيادي للمنصة...")
            
            # 🚨 تحذير سيادي: مسح شامل لضمان تحديث الحقول الجديدة
            # سيقوم بحذف كل البيانات القديمة لضمان عمل الهيكل الجديد 100%
            db.drop_all() 
            db.create_all() 
            
            # --- 🔐 1. تعميد حساب القائد العام (علي محجوب) ---
            # ملاحظة: نستخدم اسم مستخدم بالإنجليزية لضمان استقرار روابط الـ URL
            admin_user = User(
                username='Ali_Mahjoub', 
                password=generate_password_hash('123'), 
                role='admin'
            )
            db.session.add(admin_user)
            
            # --- 🏦 2. إنشاء حساب مستخدم للمورد التجريبي ---
            # في الهيكل الجديد، يجب أن يكون للمورد حساب في جدول User أولاً
            supplier_user = User(
                username='vendor_test',
                password=generate_password_hash('123'),
                role='supplier'
            )
            db.session.add(supplier_user)
            db.session.flush() # لاستخراج الـ ID قبل الحفظ النهائي لربطه بالبروفايل

            # --- 📦 3. إنشاء بروفايل المورد (التفاصيل المالية والجغرافية) ---
            test_supplier_profile = Supplier(
                user_id=supplier_user.id,
                trade_name='مؤسسة تهامة للتجارة',
                province='الحديدة',
                phone='770000000',
                is_approved=True,
                status='active',
                # تصفير المحافظ لبدء عهد مالي جديد
                wallet_balance=0.00,
                wallet_sar=0.00,
                wallet_usd=0.00,
                wallet_yer=0.00
            )
            db.session.add(test_supplier_profile)
            
            # حفظ جميع البيانات في الخزانة المركزية
            db.session.commit()
            
            print("✅ [Database] تم بناء الهيكل بنجاح. حساب القائد والمورد التجريبي جاهزان للإقلاع!")
            
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Error] فشل في عملية التطهير والتعميد التقني: {e}")

if __name__ == "__main__":
    # تشغيل عملية التهيئة (تتم تلقائياً عند كل Deployment)
    # ⚠️ تنبيه: بمجرد أن تبدأ باستقبال موردين حقيقيين، قم بتعطيل هذا السطر 
    # لكي لا يتم حذف بياناتهم عند كل إعادة تشغيل.
    initialize_sovereign_system()
    
    # ضبط المنفذ لضمان العمل على Railway
    port = int(os.environ.get("PORT", 8080))
    
    # الانطلاق بالمنصة بالترددات السيادية
    print(f"📡 منصة محجوب أونلاين تعمل الآن على المنفذ: {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
