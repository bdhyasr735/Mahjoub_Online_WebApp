# coding: utf-8
from apps import create_app
from apps.extensions import db
from apps.models.admin_db import AdminUser

def setup_sovereign_identity():
    app = create_app()
    with app.app_context():
        # التحقق هل المستخدم موجود مسبقاً لتجنب التكرار
        existing_owner = AdminUser.query.filter_by(username="mahjoub").first()
        
        if not existing_owner:
            owner = AdminUser(
                username="mahjoub",
                phone_number="779077746",
                role="Owner",
                is_active=True
            )
            # التشفير يتم هنا تلقائياً عبر الدالة التي صممناها
            owner.set_password("123") 
            
            db.session.add(owner)
            db.session.commit()
            print("✅ [تم التثبيت] هوية المالك 'mahjoub' محفوظة ومشفرة في قاعدة البيانات.")
        else:
            print("⚠️ [تنبيه] هوية المالك موجودة مسبقاً في النظام.")

if __name__ == '__main__':
    setup_sovereign_identity()
