# 📂 apps/suppliers_permissions/registry.py

# ... الكود السابق ...

# اجعل القيمة هي عنوان الرابط فقط ليقرأها النظام كـ string
LINKS = {
    "suppliers_permissions.permissions": "صلاحيات الموظفين"
}

# ملاحظة: إذا كنت تريد تخصيص الأيقونة لكل رابط، 
# يجب تحديث loop العرض في base.html، ولكن للآن استخدم MODULE_ICON:
MODULE_ICON = "fas fa-users-cog" 

# ... بقية الكود ...
