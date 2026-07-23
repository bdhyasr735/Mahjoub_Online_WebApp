# ✅ رفع الصورة إلى مكتبة قمرة
rest_api = ProductRestAPI()
image_url = rest_api.upload_image(compressed_data, image.filename)

if image_url:
    # ✅ إنشاء المنتج مع رابط الصورة
    product_data = {
        'title': name,
        'price': float(cost_price),
        'quantity': 0,
        'images': [image_url],
        'description': description,
        'status': 'DRAFT'
    }
    result = rest_api.create_product(product_data)
else:
    flash('❌ فشل رفع الصورة إلى قمرة', 'danger')
