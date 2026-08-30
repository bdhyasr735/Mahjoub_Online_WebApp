# -*- coding: utf-8 -*-
# 📂 apps/models/search_db.py

from datetime import datetime
from apps.extensions import db

class SearchLog(db.Model):
    __tablename__ = 'search_logs'

    id = db.Column(db.Integer, primary_key=True)
    query_text = db.Column(db.String(255), nullable=False, index=True)  # كلمة البحث المطلوبة
    user_type = db.Column(db.String(50), nullable=True)  # نوع المستخدم (admin, supplier, customer)
    user_id = db.Column(db.Integer, nullable=True)       # معرف المستخدم إن وجد
    results_count = db.Column(db.Integer, default=0)     # عدد النتائج التي تم العثور عليها
    ip_address = db.Column(db.String(45), nullable=True)  # عنوان IP للرصد والتحليل
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SearchLog query='{self.query_text}' results={self.results_count}>"
