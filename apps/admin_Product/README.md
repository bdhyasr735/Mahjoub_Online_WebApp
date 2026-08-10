# mudiul admin_Product - متجر محجوب أونلاين (www.mahjoub.online)

موديول مستقل للتحكم بالمنتجات والمتغيرات بالكامل داخل تطبيقات Flask.

## الهيكلة والمحتويات
```text
admin_Product/
├── __init__.py          # تعريف الـ Blueprint والمسار الرئيسي (/admin/products)
├── routes.py            # مسارات التحكم في العرض، الرفع، التعديل، والحذف
├── services.py          # كلاس ProductService وإدارة عمليات البيانات والـ SEO
└── templates/
    └── admin_Product/
        ├── products_list.html  # واجهة جدول المنتجات والفلترة والبحث
        └── product_form.html   # نافذة رفع وتعديل المنتجات والمتغيرات الديناميكية
```

## كيفية التفعيل والربط في Flask Application

في ملف `app.py` أو `main.py` الخاص بتطبيقك الأساسي:

```python
from flask import Flask
from admin_Product import admin_product_bp

app = Flask(__name__)
app.secret_key = "mahjoub-secret-key"

# تسجيل الموديول المستقل
app.register_blueprint(admin_product_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## الحقول والأقسام المدعومة
1. **البيانات الأساسية**: Title, Slug, Status (active/draft/archived), Description
2. **التسعير والمخزون**: Price, CompareAtPrice, Quantity, SKU, Barcode
3. **المتغيرات الديناميكية (Dynamic Variants)**: Name, Price, Quantity, SKU, Status
4. **الوسائط والـ SEO**: Main Image URL (`images.fileUrl`), Collections, Tags, Meta Title, Meta Description, Canonical URL.
