# -*- coding: utf-8 -*-
# 📂 apps/models/search_db.py

from datetime import datetime
from apps.extensions import db

class SearchEngineOptimization(db.Model):
    """
    جدول إدارة وتحسين محركات البحث (SEO) لصفحات المنصة، المتاجر، والمنتجات.
    يتحكم بالـ Meta Tags، الكلمات الدلالية، والـ Open Graph لضمان ظهور احترافي في محركات البحث.
    """
    __tablename__ = 'search_engine_optimizations'

    id = db.Column(db.Integer, primary_key=True)
    
    # المعرف الفرعي للصفحة أو المسار (مثل: 'home', 'supplier_login', 'products_list', أو مسار محدد)
    page_key = db.Column(db.String(150), unique=True, nullable=False, index=True)
    
    # العنوان الذي يظهر في محركات البحث (Meta Title)
    meta_title = db.Column(db.String(255), nullable=False)
    
    # الوصف المختصر الذي يظهر تحت العنوان في نتائج البحث (Meta Description)
    meta_description = db.Column(db.Text, nullable=True)
    
    # الكلمات المفتاحية مفصولة بفواصل (Meta Keywords)
    meta_keywords = db.Column(db.String(500), nullable=True)
    
    # إعدادات الـ Open Graph (مواقع التواصل الاجتماعي مثل فيسبوك وتويتر)
    og_title = db.Column(db.String(255), nullable=True)
    og_description = db.Column(db.Text, nullable=True)
    og_image = db.Column(db.String(500), nullable=True)  # رابط الصورة البارزة للمشاركة
    og_type = db.Column(db.String(50), default='website', nullable=True)
    
    # خيارات الروبوتات (Robots Index / Follow)
    allow_indexing = db.Column(db.Boolean, default=True)  # السماح لأرشفة الصفحة
    allow_following = db.Column(db.Boolean, default=True) # السماح بتتبع الروابط
    
    # تواريخ الإنشاء والتحديث
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SEO page_key='{self.page_key}' title='{self.meta_title}'>"

    @classmethod
    def get_seo_for_page(cls, page_key, default_fallback=None):
        """
        دالة مساعدة لجلب بيانات الـ SEO الخاصة بصفحة معينة من قاعدة البيانات،
        مع إرجاع القيم الافتراضية في حال عدم وجودها.
        """
        seo_record = cls.query.filter_by(page_key=page_key).first()
        if seo_record:
            return {
                'title': seo_record.meta_title,
                'description': seo_record.meta_description,
                'keywords': seo_record.meta_keywords,
                'og': {
                    'site_name': 'محجوب أونلاين',
                    'title': seo_record.og_title or seo_record.meta_title,
                    'description': seo_record.og_description or seo_record.meta_description,
                    'type': seo_record.og_type,
                    'image': seo_record.og_image
                },
                'robots': f"{'index' if seo_record.allow_indexing else 'noindex'}, {'follow' if seo_record.allow_following else 'nofollow'}"
            }
        return default_fallback
