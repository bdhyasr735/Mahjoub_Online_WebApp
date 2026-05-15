# coding: utf-8
from apps import db # استيراد db من القلب المركزي

# استيراد الجداول لضمان تسجيلها في محرك SQLAlchemy
from apps.models.admin_db import AdminUser
from apps.models.supplier_db import Supplier
