# -*- coding: utf-8 -*-
# 📂 apps/models/supplier_staff_db.py

import os
from datetime import datetime
from cryptography.fernet import Fernet
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event, update
from apps.extensions import db


class SupplierStaff(db.Model, UserMixin):
    __tablename__ = 'supplier_staff'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False)
    staff_code = db.Column(db.String(50), unique=True, nullable=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), default='staff')
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    _full_name_enc = db.Column(db.String(255), nullable=True)
    _email_enc = db.Column(db.String(255), nullable=True)
    _phone_enc = db.Column(db.String(255), nullable=True)
    search_phone = db.Column(db.String(20), nullable=True)
    _position_enc = db.Column(db.String(255), nullable=True)
    _address_enc = db.Column(db.String(500), nullable=True)

    password_hash = db.Column(db.String(255), nullable=True)

    supplier = db.relationship('Supplier', back_populates='staff_members')

    @staticmethod
    def _get_key():
        key = os.environ.get('ENCRYPTION_KEY')
        return key.encode() if key else b'w1Kk9P7zY5mZg4tE8Lp2nJvR6cXsA9qB0xU3jH5oI8Vq='

    def _encrypt(self, value):
        if not value:
            return None
        try:
            return Fernet(self._get_key()).encrypt(str(value).encode()).decode()
        except:
            return None

    def _decrypt(self, value):
        if not value:
            return None
        try:
            return Fernet(self._get_key()).decrypt(value.encode()).decode()
        except:
            return None

    @property
    def full_name(self):
        return self._decrypt(self._full_name_enc)

    @full_name.setter
    def full_name(self, value):
        self._full_name_enc = self._encrypt(value)

    @property
    def email(self):
        return self._decrypt(self._email_enc)

    @email.setter
    def email(self, value):
        self._email_enc = self._encrypt(value)

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
            self._phone_enc = None
            self.search_phone = None

    @property
    def position(self):
        return self._decrypt(self._position_enc)

    @position.setter
    def position(self, value):
        self._position_enc = self._encrypt(value)

    @property
    def address(self):
        return self._decrypt(self._address_enc)

    @address.setter
    def address(self, value):
        self._address_enc = self._encrypt(value)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'staff_code': self.staff_code,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'position': self.position,
            'role': self.role,
            'status': self.status
        }

    def __repr__(self):
        return f"<SupplierStaff {self.id}: {self.username}>"


@event.listens_for(SupplierStaff, 'after_insert')
def receive_staff_after_insert(mapper, connection, target):
    new_staff_code = f"SUP963{target.supplier_id}-ST{target.id}"
    connection.execute(
        update(SupplierStaff).where(SupplierStaff.id == target.id).values(staff_code=new_staff_code)
    )
