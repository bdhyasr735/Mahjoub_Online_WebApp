# coding: utf-8
# تجميع وإشهار النماذج لسهولة الاستيراد من خارج حزمة models

from apps.models.admin_db import AdminUser
from apps.models.supplier_db import Supplier
# إضافة الموديل الجديد هنا:
from apps.models.settlements_db import AdminSettlement 

# يفضل أيضاً إضافة موديل المحفظة إذا كان موجوداً في ملف مستقل، 
# تأكد من استيراد كل شيء تحتاجه هنا لتجنب أي مشاكل عند الاستيراد.
