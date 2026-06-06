# 📂 run.py
# ... (استيراداتك السابقة) ...

def ensure_admin():
    """التأكد من وجود المدير السيادي بتشفير آمن."""
    admin = AdminUser.query.filter_by(username="محجوب").first()
    
    if not admin:
        new_admin = AdminUser(username="محجوب", phone_number="0000000000", role='Owner')
        # استخدام دالة التشفير الموجودة في الموديل (set_password)
        new_admin.set_password("123") 
        db.session.add(new_admin)
        db.session.commit()
        print("✅ تم إنشاء الهوية السيادية (محجوب) بكلمة مرور مشفرة.")
    else:
        print("ℹ️ الهوية السيادية (محجوب) موجودة مسبقاً.")

# داخل دالة auto_repair_db() استدعِ هذه الدالة:
# ensure_admin()
