from core import db  # استيراد كائن db المعرف في __init__.py الخاص بـ core
from datetime import datetime
from sqlalchemy import inspect

class Vendor(db.Model):
    __tablename__ = 'vendors'

    # --- الحقول الأساسية ---
    id = db.Column(db.Integer, primary_key=True)
    
    # الربط مع المستخدم (User Model)
    # هذا هو العمود الذي تسبب في الخطأ لأنه مفقود في قاعدة البيانات الحالية
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # --- بيانات الهوية والملك والوثائق ---
    owner_name = db.Column(db.String(255), nullable=False)
    id_type = db.Column(db.String(100), nullable=False)
    id_card_number = db.Column(db.String(50), nullable=False)
    id_image_path = db.Column(db.String(500), nullable=True) 
    
    # --- بيانات المنشأة والنشاط ---
    trade_name = db.Column(db.String(255), nullable=False)
    activity_type = db.Column(db.String(100), nullable=False)
    
    # --- البيانات الجغرافية والاتصال ---
    province = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    address_detail = db.Column(db.String(500), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    # --- الربط المالي والسيادي ---
    e_wallet = db.Column(db.String(100), unique=True, nullable=False)
    fin_type = db.Column(db.String(50), default='banks')
    bank_name = db.Column(db.String(150), nullable=False)
    bank_acc = db.Column(db.String(100), nullable=False)

    # --- بيانات النظام ---
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Vendor {self.trade_name} - Sovereign ID: {self.e_wallet}>"

# --- وظيفة إصلاح الترسانة تلقائياً ---
def check_and_upgrade_vendor_table():
    """
    تقوم هذه الدالة بفحص جدول الموردين وإضافة الأعمدة الناقصة تلقائياً
    لتجنب خطأ UndefinedColumn
    """
    with db.engine.connect() as conn:
        inspector = inspect(db.engine)
        existing_columns = [c['name'] for c in inspector.get_columns('vendors')]
        
        # قائمة بالأعمدة الحساسة التي قد تكون مفقودة
        required_columns = {
            'user_id': 'INTEGER',
            'province': 'VARCHAR(100)',
            'district': 'VARCHAR(100)',
            'id_type': 'VARCHAR(100)',
            'fin_type': 'VARCHAR(50)',
            'address_detail': 'VARCHAR(500)',
            'phone': 'VARCHAR(20)'
        }
        
        for col, col_type in required_columns.items():
            if col not in existing_columns:
                print(f"🛠️ جاري ترقية الترسانة: إضافة عمود {col}...")
                conn.execute(db.text(f'ALTER TABLE vendors ADD COLUMN {col} {col_type};'))
                conn.commit()
