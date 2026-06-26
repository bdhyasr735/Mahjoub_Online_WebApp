# coding: utf-8
# 📂 apps/models/supplier_staff_db.py

from apps.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class SupplierStaff(db.Model):
    __tablename__ = 'supplier_staff'
    
    # [صمام الأمان]: دمج الاندكسات في مكان واحد لمنع التكرار (DuplicateIndex)
    __table_args__ = (
        db.Index('idx_staff_supplier_id', 'supplier_id'),
        db.Index('idx_staff_username', 'username'),
        db.Index('idx_staff_email', 'email'),
        db.Index('idx_staff_role', 'role'),
        db.Index('idx_staff_active', 'is_active'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='worker')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # [المسار الكامل]: لمنع خطأ Multiple classes found
    supplier = db.relationship(
        'apps.models.supplier_db.Supplier', 
        back_populates='staff_members'
    )

    # [التشفير السيادي]: ترقية خوارزمية التشفير
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Staff {self.username} | Role: {self.role}>'
