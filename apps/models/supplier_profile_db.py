# coding: utf-8
# 📂 apps/models/supplier_profile_db.py - (البيانات التجارية المتقدمة للموردين)

from apps.extensions import db

class SupplierProfile(db.Model):
    __tablename__ = 'supplier_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # الربط المفتاحي الحوكمي مع الحساب الموحد
    user_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), unique=True, nullable=False)
    wallet_code = db.Column(db.String(50), nullable=True)

    # --- الحقول التجارية المشفرة الخاصة بالموردين فقط ---
    trade_name_enc = db.Column(db.String(255), nullable=True) 
    owner_name_enc = db.Column(db.String(255), nullable=True)
    id_type_enc = db.Column(db.String(255), nullable=True)
    supply_category_enc = db.Column(db.String(255), nullable=True)
    province_enc = db.Column(db.String(255), nullable=True)
    district_enc = db.Column(db.String(255), nullable=True)
    address_detail_enc = db.Column(db.Text, nullable=True)
    financial_company_enc = db.Column(db.String(255), nullable=True)
    bank_name_enc = db.Column(db.String(255), nullable=True)
    bank_acc_enc = db.Column(db.String(255), nullable=True)

    # العلاقات البرمجية: تم استخدام الاستدعاء الكسول (lazy='joined') لمنع أي تعليق أو تضارب في المعالج
    user = db.relationship('AdminUser', back_populates='supplier_profile', lazy='joined')

# 🔗 كسر جمود الـ Mapper وحقن الموديل الإداري الموحد في ذاكرة SQLAlchemy فوراً عند استدعاء هذا الملف
from apps.models.admin_db import AdminUser
