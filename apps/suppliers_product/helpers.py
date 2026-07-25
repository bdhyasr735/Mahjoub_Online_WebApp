# coding: utf-8
# 📂 apps/suppliers_product/helpers.py

from io import BytesIO
from PIL import Image
import logging
import math
import re

logger = logging.getLogger(__name__)


# ============================================
# 1. ضغط الصور
# ============================================

def compress_image(image_data, max_size=(800, 800), quality=70):
    """
    ضغط وتقليل حجم الصورة مع الحفاظ على الخلفية البيضاء للصور الشفافة (PNG/RGBA)
    
    Args:
        image_data: بيانات الصورة (bytes)
        max_size: الحد الأقصى للأبعاد (width, height)
        quality: جودة الضغط (1-100)
    
    Returns:
        bytes: بيانات الصورة المضغوطة
    """
    try:
        img = Image.open(BytesIO(image_data))
        
        # معالجة الصور الشفافة لمنع التحلل إلى اللون الأسود عند تحويلها لـ JPEG
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # إعادة الحجم مع الحفاظ على أبعاد الصورة
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"❌ خطأ أثناء ضغط الصورة: {e}")
        return image_data


# ============================================
# 2. الترقيم (Pagination)
# ============================================

def paginate(items, page=1, per_page=20, per_page_options=None):
    """
    تقسيم القائمة إلى صفحات بشكل آمن
    
    Args:
        items: القائمة الكاملة
        page: رقم الصفحة الحالية
        per_page: عدد العناصر في كل صفحة
        per_page_options: خيارات عدد العناصر لكل صفحة
    
    Returns:
        dict: بيانات الترقيم
    """
    page = max(1, int(page) if str(page).isdigit() else 1)
    per_page = max(1, int(per_page) if str(per_page).isdigit() else 20)
    
    total = len(items) if items else 0
    total_pages = max(1, (total + per_page - 1) // per_page) if total > 0 else 1
    
    # التأكد من أن الصفحة لا تتجاوز العدد الكلي
    page = min(page, total_pages) if page > 0 else 1
    
    start = (page - 1) * per_page
    end = min(start + per_page, total)
    
    # قائمة الصفحات للعرض (مع ...)
    pages_list = get_pages_list(page, total_pages)
    
    return {
        'items': items[start:end] if items else [],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': total_pages,
        'pages_list': pages_list,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None,
        'start': start + 1 if total > 0 else 0,
        'end': end,
        'per_page_options': per_page_options or [10, 20, 50, 100]
    }


def get_pages_list(current_page, total_pages, max_display=5):
    """
    إنشاء قائمة الصفحات للعرض مع علامة ...
    
    Args:
        current_page: الصفحة الحالية
        total_pages: إجمالي الصفحات
        max_display: الحد الأقصى لعدد الصفحات المعروضة
    
    Returns:
        list: قائمة الصفحات
    """
    if total_pages <= max_display:
        return list(range(1, total_pages + 1))
    
    pages = []
    half = max_display // 2
    
    if current_page <= half + 1:
        pages = list(range(1, max_display))
        pages.append('...')
        pages.append(total_pages)
    elif current_page >= total_pages - half:
        pages = [1, '...']
        pages.extend(range(total_pages - max_display + 2, total_pages + 1))
    else:
        pages = [1, '...']
        pages.extend(range(current_page - half, current_page + half + 1))
        pages.append('...')
        pages.append(total_pages)
    
    return pages


# ============================================
# 3. البحث والفلترة
# ============================================

def filter_by_search(items, search, key='title'):
    """
    فلترة العناصر حسب البحث (يدعم البحث المباشر وفي العناصر المدمجة مثل 'product' أو 'mapping')
    
    Args:
        items: قائمة العناصر
        search: مصطلح البحث
        key: المفتاح الأساسي للبحث
    
    Returns:
        list: القائمة المفلترة
    """
    if not search or not items:
        return items or []
    
    search_lower = str(search).strip().lower()

    filtered = []
    for item in items:
        # البحث في المستوى الأعلى أولاً
        val = item.get(key)
        
        # البحث داخل كائن المنتج المتداخل إن وجد
        if val is None and isinstance(item.get('product'), dict):
            product_dict = item['product']
            val = product_dict.get(key) or product_dict.get('name') or product_dict.get('title')
        
        # البحث بواسطة SKU
        sku_val = item.get('sku') or (item.get('product', {}).get('sku') if isinstance(item.get('product'), dict) else None)
        
        # البحث بواسطة QID
        qid_val = item.get('qid') or (item.get('mapping', {}).get('qid') if isinstance(item.get('mapping'), dict) else None)

        target_text = f"{str(val or '')} {str(sku_val or '')} {str(qid_val or '')}".lower()
        if search_lower in target_text:
            filtered.append(item)

    return filtered


# ============================================
# 4. فلترة حسب الحالة
# ============================================

def filter_by_status(items, status):
    """
    فلترة العناصر حسب الحالة
    
    Args:
        items: قائمة العناصر
        status: الحالة المطلوبة
    
    Returns:
        list: القائمة المفلترة
    """
    if not items or not status or status == 'all':
        return items or []
    
    status = status.upper()
    filtered = []
    
    for item in items:
        # الحصول على الحالة من العنصر
        item_status = item.get('status')
        if item_status is None and isinstance(item.get('product'), dict):
            item_status = item['product'].get('status')
        if item_status is None and isinstance(item.get('mapping'), dict):
            item_status = item['mapping'].get('status')
        
        if str(item_status).upper() == status:
            filtered.append(item)
    
    return filtered


# ============================================
# 5. الحصول على لون البادج
# ============================================

def get_status_badge(status):
    """
    الحصول على لون البادج حسب الحالة بشكل آمن
    
    Args:
        status: حالة المنتج
    
    Returns:
        str: اسم اللون (success, warning, danger, secondary, info)
    """
    if not status:
        return 'secondary'
    
    status_map = {
        'ACTIVE': 'success',
        'PUBLISHED': 'success',
        'DRAFT': 'warning',
        'PENDING': 'info',
        'INACTIVE': 'danger',
        'ARCHIVED': 'secondary',
        'REJECTED': 'danger',
        'DELETED': 'dark'
    }
    
    return status_map.get(str(status).strip().upper(), 'secondary')


# ============================================
# 6. الحصول على نص الحالة
# ============================================

def get_status_text(status):
    """
    الحصول على النص العربي للحالة
    
    Args:
        status: حالة المنتج
    
    Returns:
        str: النص العربي
    """
    if not status:
        return 'غير معروف'
    
    status_map = {
        'ACTIVE': 'نشط',
        'PUBLISHED': 'منشور',
        'DRAFT': 'مسودة',
        'PENDING': 'قيد المراجعة',
        'INACTIVE': 'غير نشط',
        'ARCHIVED': 'مؤرشف',
        'REJECTED': 'مرفوض',
        'DELETED': 'محذوف'
    }
    
    return status_map.get(str(status).strip().upper(), status)


# ============================================
# 7. استخراج البيانات من المنتج
# ============================================

def extract_product_data(product):
    """
    استخراج البيانات الأساسية من المنتج (يدعم هيكل GraphQL)
    
    Args:
        product: كائن المنتج
    
    Returns:
        dict: البيانات الأساسية
    """
    if not product:
        return {}
    
    # إذا كان المنتج يحتوي على حقل 'product' (من الـ mapping)
    if isinstance(product, dict) and 'product' in product:
        prod = product['product']
    else:
        prod = product
    
    return {
        'qid': prod.get('qid') or product.get('qid'),
        'name': prod.get('name') or prod.get('title') or 'منتج بدون اسم',
        'title': prod.get('name') or prod.get('title') or 'منتج بدون اسم',
        'description': prod.get('description', ''),
        'price': prod.get('price', 0),
        'quantity': prod.get('quantity', 0),
        'sku': prod.get('sku', ''),
        'status': prod.get('status', 'DRAFT'),
        'images': prod.get('images', []),
        'mainImage': prod.get('mainImage', {}),
        'variants': prod.get('variants', []),
        'inventory': prod.get('inventory', {})
    }


# ============================================
# 8. تنسيق السعر
# ============================================

def format_price(price, currency='SAR'):
    """
    تنسيق السعر
    
    Args:
        price: السعر
        currency: العملة
    
    Returns:
        str: السعر المنسق
    """
    try:
        price = float(price)
        return f"{price:,.2f} {currency}"
    except (ValueError, TypeError):
        return f"0.00 {currency}"


# ============================================
# 9. توليد SKU
# ============================================

def generate_sku(prefix='PRD'):
    """
    توليد SKU تلقائي
    
    Args:
        prefix: بادئة SKU
    
    Returns:
        str: SKU
    """
    import random
    random_num = str(random.randint(100000, 999999))
    return f"{prefix[:3].upper()}-{random_num}"


# ============================================
# 10. التحقق من صحة البيانات
# ============================================

def validate_product_data(data):
    """
    التحقق من صحة بيانات المنتج
    
    Args:
        data: بيانات المنتج
    
    Returns:
        tuple: (is_valid, errors)
    """
    errors = []
    
    # اسم المنتج مطلوب
    title = data.get('title', '').strip()
    if not title:
        errors.append('اسم المنتج مطلوب')
    elif len(title) < 3:
        errors.append('اسم المنتج يجب أن يكون 3 أحرف على الأقل')
    
    # السعر مطلوب
    price = data.get('price')
    if price is None or price == '':
        errors.append('السعر مطلوب')
    else:
        try:
            if float(price) < 0:
                errors.append('السعر يجب أن يكون أكبر من أو يساوي 0')
        except (ValueError, TypeError):
            errors.append('السعر يجب أن يكون رقم صحيح')
    
    # الكمية يجب أن تكون رقم
    quantity = data.get('quantity')
    if quantity is not None and quantity != '':
        try:
            if int(quantity) < 0:
                errors.append('الكمية يجب أن تكون أكبر من أو يساوي 0')
        except (ValueError, TypeError):
            errors.append('الكمية يجب أن تكون رقم صحيح')
    
    return len(errors) == 0, errors


# ============================================
# 11. إحصائيات المنتجات
# ============================================

def get_product_stats_from_list(products):
    """
    حساب إحصائيات المنتجات من القائمة
    
    Args:
        products: قائمة المنتجات
    
    Returns:
        dict: الإحصائيات
    """
    if not products:
        return {
            'total': 0,
            'published': 0,
            'draft': 0,
            'pending': 0,
            'rejected': 0,
            'archived': 0
        }
    
    total = len(products)
    published = 0
    draft = 0
    pending = 0
    rejected = 0
    archived = 0
    
    for item in products:
        # الحصول على الحالة
        if isinstance(item, dict) and 'product' in item:
            status = item['product'].get('status', '')
        else:
            status = item.get('status', '')
        
        status = str(status).upper()
        if status == 'PUBLISHED':
            published += 1
        elif status == 'DRAFT':
            draft += 1
        elif status == 'PENDING':
            pending += 1
        elif status == 'REJECTED':
            rejected += 1
        elif status == 'ARCHIVED':
            archived += 1
    
    return {
        'total': total,
        'published': published,
        'draft': draft,
        'pending': pending,
        'rejected': rejected,
        'archived': archived
    }
