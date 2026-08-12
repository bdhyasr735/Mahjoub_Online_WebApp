# coding: utf-8
# 📂 apps/models/supplier_profile_db.py

from apps.extensions import db

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    icon = db.Column(db.String(50), nullable=True)  # أيقونة FontAwesome مثلاً

    profiles = db.relationship('SupplierProfile', back_populates='category_rel', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'


class Bank(db.Model):
    __tablename__ = 'banks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    icon = db.Column(db.String(50), nullable=True)

    profiles = db.relationship('SupplierProfile', back_populates='bank_rel', lazy='dynamic')

    def __repr__(self):
        return f'<Bank {self.name}>'


class FinancialCompany(db.Model):
    __tablename__ = 'financial_companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=True)  # مثل "تمويل", "استثمار", إلخ

    profiles = db.relationship('SupplierProfile', back_populates='company_rel', lazy='dynamic')

    def __repr__(self):
        return f'<FinancialCompany {self.name}>'
