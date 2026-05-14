from datetime import datetime
from apps import db  # استيراد db من مجلد التطبيق الرئيسي المشترك

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    sovereign_id = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50))
    owner_name = db.Column(db.String(100))
    trade_name = db.Column(db.String(100), unique=True)
    shop_phone = db.Column(db.String(20))
    province = db.Column(db.String(50))
    district = db.Column(db.String(50))
    address_detail = db.Column(db.Text)
    finance_type = db.Column(db.String(50))
    bank_name = db.Column(db.String(100))
    bank_account = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 💡 حركة ذكية تلقائية: فحص وإضافة الأعمدة الناقصة في السيرفر فور الإقلاع لضمان عدم حدوث خطأ UndefinedColumn
def check_and_upgrade_db(app):
    with app.app_context():
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('suppliers')]
            
            # الأعمدة الجديدة المراد التحقق منها
            expected_columns = {
                'category': 'VARCHAR(50)',
                'finance_type': 'VARCHAR(50)',
                'bank_name': 'VARCHAR(100)',
                'bank_account': 'VARCHAR(100)'
            }
            
            for col_name, col_type in expected_columns.items():
                if col_name not in columns:
                    print(f"🔧 [DB Upgrade] Adding missing column: {col_name}")
                    db.session.execute(text(f"ALTER TABLE suppliers ADD COLUMN {col_name} {col_type};"))
                    db.session.commit()
        except Exception as e:
            print(f"⚠️ [DB Upgrade Warning]: {e}")
