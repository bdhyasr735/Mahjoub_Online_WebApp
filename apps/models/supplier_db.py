# -*- coding: utf-8 -*-
# 📂 apps/models/supplier_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event, update
from apps.extensions import db


class Supplier(db.Model, UserMixin):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    supplier_code = db.Column(db.String(50), unique=True, nullable=True)
    owner_name = db.Column(db.String(150), nullable=True)
    trade_name = db.Column(db.String(150), nullable=True)
    store_name = db.Column(db.String(150), nullable=True)

    _phone_enc = db.Column(db.String(255), nullable=False)
    search_phone = db.Column(db.String(20), unique=True, nullable=True)

    password_hash = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='active')
    rank = db.Column(db.String(20), default='bronze')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    wallet = db.relationship('SupplierWallet', back_populates='supplier', uselist=False)
    staff_members = db.relationship('SupplierStaff', back_populates='supplier')

    @staticmethod
    def _get_key():
        key = os.environ.get('ENCRYPTION_KEY')
        return key.encode() if key else b'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq='

    def _encrypt(self, value):
        if not value:
            return ""
        f = Fernet(self._get_key())
        return f.encrypt(str(value).encode()).decode()

    def _decrypt(self, value):
        if not value:
            return None
        try:
            f = Fernet(self._get_key())
            return f.decrypt(value.encode()).decode()
        except:
            return None

    @property
    def phone(self):
        return self._decrypt(self._phone_enc)

    @phone.setter
    def phone(self, value):
        if value:
            str_val = str(value)
            digits_only = "".join(filter(str.isdigit, str_val))
            clean_9 = digits_only[-9:] if len(digits_only) >= 9 else digits_only
            self._phone_enc = self._encrypt(str_val)
            self.search_phone = clean_9
        else:
            self._phone_enc = self._encrypt("")
            self.search_phone = None

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'supplier_code': self.supplier_code,
            'owner_name': self.owner_name,
            'trade_name': self.trade_name,
            'store_name': self.store_name,
            'phone': self.phone,
            'status': self.status,
            'rank': self.rank,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Supplier {self.id}: {self.username}>"


@event.listens_for(Supplier, 'after_insert')
def receive_after_insert(mapper, connection, target):
    new_supplier_code = f"SUP-963{target.id}"
    connection.execute(
        update(Supplier).where(Supplier.id == target.id).values(supplier_code=new_supplier_code)
    )
